"""
Merge equivalent checks in BatchCheck (the `merge_equivalent_checks` option).

Checks that are certain to get the same answer are sent once, and the answer is
copied back to every original check. Rules: https://github.com/openfga/rfcs/pull/40
"""

import math
import re
import struct

from collections import Counter
from dataclasses import dataclass

from openfga_sdk.client.models.batch_check_item import ClientBatchCheckItem
from openfga_sdk.client.models.batch_check_single_response import (
    ClientBatchCheckSingleResponse,
)
from openfga_sdk.exceptions import FgaValidationException
from openfga_sdk.models.authorization_model import AuthorizationModel
from openfga_sdk.models.batch_check_single_result import BatchCheckSingleResult
from openfga_sdk.models.check_error import CheckError
from openfga_sdk.models.userset import Userset


CORRELATION_ID_PATTERN = re.compile(r"^[\w\d-]{1,36}$", re.ASCII)

_MISSING = ("missing",)


class _Unmergeable(Exception):
    """A value the SDK can't compare exactly, so the check is sent as is."""


@dataclass
class EquivalentCheckGroup:
    """
    A check to send, and the original checks it answers.
    """

    check: ClientBatchCheckItem
    members: list[ClientBatchCheckItem]


def merge_enabled(options: dict | None) -> bool:
    """
    Return whether the `merge_equivalent_checks` option is on. Missing or None means off,
    like other options. Raise for any other non-bool, so "true" can't silently leave it off.
    """
    value = (options or {}).get("merge_equivalent_checks")
    if value is not None and not isinstance(value, bool):
        raise FgaValidationException(
            f"merge_equivalent_checks must be a bool, got {type(value).__name__}"
        )
    return value is True


def validate_correlation_ids(checks: list[ClientBatchCheckItem]) -> None:
    """
    Raise if a correlation ID doesn't match the API rule, or is used twice.
    """
    seen: set[str] = set()
    for check in checks:
        correlation_id = check.correlation_id
        # fullmatch, since `$` alone would also accept a trailing newline
        if not isinstance(correlation_id, str) or not CORRELATION_ID_PATTERN.fullmatch(
            correlation_id
        ):
            raise FgaValidationException(
                f"correlation_id ({correlation_id}) is invalid: it must match {CORRELATION_ID_PATTERN.pattern}"
            )
        if correlation_id in seen:
            raise FgaValidationException(
                f"Duplicate correlation_id ({correlation_id}) provided"
            )
        seen.add(correlation_id)


def unmerged(checks: list[ClientBatchCheckItem]) -> list[EquivalentCheckGroup]:
    """
    One group per check, sent as is.
    """
    return [EquivalentCheckGroup(check=check, members=[check]) for check in checks]


def resolve(
    model: AuthorizationModel, checks: list[ClientBatchCheckItem]
) -> list[EquivalentCheckGroup]:
    """
    Group checks that are certain to get the same answer, and build the checks to send.

    The result is deterministic: the same model and checks, in the same order, give the
    same groups and IDs. Each group is placed at the position of its first check.
    """
    types = {
        type_definition.type: type_definition.relations or {}
        for type_definition in model.type_definitions or []
    }

    entries: list[tuple[str, ClientBatchCheckItem | tuple]] = []
    groups: dict[tuple, list[ClientBatchCheckItem]] = {}
    finals: dict[tuple, str] = {}

    for check in checks:
        final_relation = _final_relation(types, check)
        key = None
        if final_relation is not None:
            try:
                key = (
                    final_relation,
                    check.user,
                    check.object,
                    _context_key(check.context),
                    _contextual_tuples_key(check.contextual_tuples),
                )
            except _Unmergeable:
                key = None

        if key is None:
            entries.append(("as_is", check))
            continue

        if key not in groups:
            groups[key] = []
            finals[key] = final_relation
            entries.append(("group", key))
        groups[key].append(check)

    caller_ids = {check.correlation_id for check in checks}
    next_number = 1
    result: list[EquivalentCheckGroup] = []

    for kind, entry in entries:
        if kind == "as_is":
            result.append(EquivalentCheckGroup(check=entry, members=[entry]))
            continue

        members = groups[entry]
        first = members[0]
        if len(members) == 1:
            correlation_id = first.correlation_id
        else:
            while f"merged-{next_number}" in caller_ids:
                next_number += 1
            correlation_id = f"merged-{next_number}"
            next_number += 1

        result.append(
            EquivalentCheckGroup(
                check=ClientBatchCheckItem(
                    user=first.user,
                    relation=finals[entry],
                    object=first.object,
                    correlation_id=correlation_id,
                    contextual_tuples=first.contextual_tuples,
                    context=first.context,
                ),
                members=members,
            )
        )

    return result


def expand(
    checks: list[ClientBatchCheckItem],
    groups: list[EquivalentCheckGroup],
    results: dict[str, BatchCheckSingleResult],
) -> list[ClientBatchCheckSingleResponse]:
    """
    Copy each group's answer to every check in the group, in the order of `checks`.

    A group with no answer gives an error for every check in it. Answers with unknown
    correlation IDs are ignored.
    """
    responses: dict[str, ClientBatchCheckSingleResponse] = {}

    for group in groups:
        sent_id = group.check.correlation_id
        result = results.get(sent_id)
        allowed = result.allowed if result is not None else None
        error = (
            result.error
            if result is not None
            else CheckError(
                message=f"No result returned for correlation_id ({sent_id})"
            )
        )

        for member in group.members:
            responses[member.correlation_id] = ClientBatchCheckSingleResponse(
                allowed=allowed,
                request=member,
                correlation_id=member.correlation_id,
                error=error,
            )

    return [responses[check.correlation_id] for check in checks]


def _alias_target(rewrite: Userset | None) -> str | None:
    """
    Return the relation an alias points to, or None if the rewrite isn't a lone computedUserset.
    """
    if rewrite is None or rewrite.computed_userset is None:
        return None

    if (
        rewrite.this is not None
        or rewrite.tuple_to_userset is not None
        or rewrite.union is not None
        or rewrite.intersection is not None
        or rewrite.difference is not None
    ):
        return None

    target = rewrite.computed_userset
    if target.object or not target.relation:
        return None

    return target.relation


def _alias_chain(relations: dict[str, Userset], relation: str) -> list[str] | None:
    """
    Follow aliases from `relation`. Return every relation on the way, ending at the final
    relation, or None if the chain points to a missing relation or loops.
    """
    chain = [relation]
    while True:
        if chain[-1] not in relations:
            return None

        target = _alias_target(relations[chain[-1]])
        if target is None:
            return chain

        if target in chain:
            return None

        chain.append(target)


def _final_relation(types: dict[str, dict[str, Userset]], check) -> str | None:
    """
    Return the relation to send the check with, or None to send it as is.
    """
    if not all(
        isinstance(value, str) for value in (check.user, check.relation, check.object)
    ):
        return None

    object_type, separator, object_id = check.object.partition(":")
    if not separator or object_type not in types:
        return None

    relations = types[object_type]
    if check.relation not in relations:
        return None

    user_type, separator, user_rest = check.user.partition(":")
    if not separator or user_type not in types:
        return None

    user_id, userset_separator, user_relation = user_rest.partition("#")
    if userset_separator and user_relation not in types[user_type]:
        return None

    chain = _alias_chain(relations, check.relation)
    if chain is None:
        return None

    # The server says a userset always has its own relation on its own object, at every
    # step of a chain, so a merged check could get a different answer.
    if (
        userset_separator
        and (user_type, user_id) == (object_type, object_id)
        and user_relation in chain
    ):
        return None

    # The server's answer can depend on which of these tuples it reads first.
    tuple_keys = [
        (contextual_tuple.user, contextual_tuple.relation, contextual_tuple.object)
        for contextual_tuple in check.contextual_tuples or []
    ]
    if len(set(tuple_keys)) != len(tuple_keys):
        return None

    return chain[-1]


def _context_key(context) -> tuple:
    if context is None:
        return _MISSING

    if not isinstance(context, dict):
        raise _Unmergeable()

    return _canonical(context)


def _contextual_tuples_key(contextual_tuples) -> tuple | frozenset:
    if contextual_tuples is None:
        return _MISSING

    items = []
    for contextual_tuple in contextual_tuples:
        condition = contextual_tuple.condition
        condition_key = _MISSING
        if condition is not None:
            condition_key = (condition.name, _context_key(condition.context))

        items.append(
            (
                contextual_tuple.user,
                contextual_tuple.relation,
                contextual_tuple.object,
                condition_key,
            )
        )

    return frozenset(Counter(items).items())


def _canonical(value) -> tuple:
    """
    A hashable form of a JSON value, equal only for values the server sees as equal.
    Numbers compare as doubles, including the sign of zero.
    """
    if value is None:
        return ("null",)

    if isinstance(value, bool):
        return ("bool", value)

    if isinstance(value, int | float):
        try:
            number = float(value)
        except OverflowError as err:
            raise _Unmergeable() from err

        if not math.isfinite(number):
            raise _Unmergeable()

        return ("number", struct.pack(">d", number))

    if isinstance(value, str):
        return ("string", value)

    if isinstance(value, list):
        return ("list", tuple(_canonical(item) for item in value))

    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise _Unmergeable()

        return (
            "object",
            frozenset((key, _canonical(item)) for key, item in value.items()),
        )

    raise _Unmergeable()
