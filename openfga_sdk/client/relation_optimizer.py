from dataclasses import dataclass

from openfga_sdk.client.models.batch_check_item import ClientBatchCheckItem
from openfga_sdk.models.authorization_model import AuthorizationModel
from openfga_sdk.models.userset import Userset


@dataclass(frozen=True)
class RelationCheckGroup:
    """BatchCheck items that can share one relation evaluation."""

    relation: str
    indexes: tuple[int, ...]


def build_relation_aliases(
    authorization_model: AuthorizationModel,
) -> dict[str, dict[str, str]]:
    """Build canonical targets for pure computed-userset relation aliases."""
    aliases_by_type: dict[str, dict[str, str]] = {}

    for type_definition in authorization_model.type_definitions or []:
        relations = type_definition.relations or {}
        direct_aliases = {
            relation: target
            for relation, rewrite in relations.items()
            if (target := _pure_computed_userset_target(rewrite)) is not None
            and target in relations
        }

        canonical_aliases: dict[str, str] = {}
        for relation in direct_aliases:
            target = _resolve_alias(relation, direct_aliases)
            if target is not None and target != relation:
                canonical_aliases[relation] = target

        aliases_by_type[type_definition.type] = canonical_aliases

    return aliases_by_type


def group_batch_checks(
    checks: list[ClientBatchCheckItem], aliases_by_type: dict[str, dict[str, str]]
) -> list[RelationCheckGroup]:
    """Group checks that differ only by pure aliases of the same relation."""
    candidates: list[tuple[str, ClientBatchCheckItem, list[int]]] = []

    for index, check in enumerate(checks):
        object_type, separator, _ = check.object.partition(":")
        aliases = aliases_by_type.get(object_type, {}) if separator else {}
        target = aliases.get(check.relation, check.relation)

        for candidate_target, representative, indexes in candidates:
            if candidate_target == target and _same_check_inputs(check, representative):
                indexes.append(index)
                break
        else:
            candidates.append((target, check, [index]))

    groups: list[RelationCheckGroup] = []
    for target, _, indexes in candidates:
        if len(indexes) > 1 and any(
            checks[index].relation != target for index in indexes
        ):
            groups.append(RelationCheckGroup(relation=target, indexes=tuple(indexes)))
        else:
            groups.extend(
                RelationCheckGroup(
                    relation=checks[index].relation,
                    indexes=(index,),
                )
                for index in indexes
            )

    groups.sort(key=lambda group: group.indexes[0])
    return groups


def _same_check_inputs(left: ClientBatchCheckItem, right: ClientBatchCheckItem) -> bool:
    """Return whether two checks differ only in relation and correlation ID."""
    return (
        left.user == right.user
        and left.object == right.object
        and left.context == right.context
        and left.contextual_tuples == right.contextual_tuples
    )


def _pure_computed_userset_target(rewrite: Userset) -> str | None:
    """Return the target when a rewrite is only a same-object computed userset."""
    computed_userset = rewrite.computed_userset
    if computed_userset is None or not computed_userset.relation:
        return None

    if any(
        value is not None
        for value in (
            rewrite.this,
            rewrite.tuple_to_userset,
            rewrite.union,
            rewrite.intersection,
            rewrite.difference,
        )
    ):
        return None

    if computed_userset.object not in (None, ""):
        return None

    return computed_userset.relation


def _resolve_alias(relation: str, direct_aliases: dict[str, str]) -> str | None:
    """Resolve an alias chain, returning none when it contains a cycle."""
    visited = set()
    current = relation

    while current in direct_aliases:
        if current in visited:
            return None
        visited.add(current)
        current = direct_aliases[current]

    return current
