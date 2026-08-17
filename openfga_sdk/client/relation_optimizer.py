from dataclasses import dataclass

from openfga_sdk.models.authorization_model import AuthorizationModel
from openfga_sdk.models.userset import Userset


@dataclass(frozen=True)
class RelationCheckGroup:
    """Relations that can share a single authorization check."""

    relation: str
    indexes: tuple[int, ...]


def is_concrete_user(user: str) -> bool:
    """Return whether a user string represents one concrete object."""
    return user != "*" and not user.endswith(":*") and "#" not in user


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


def group_relations(
    relations: list[str], aliases: dict[str, str]
) -> list[RelationCheckGroup]:
    """Group requested relations by their canonical evaluation target."""
    indexes_by_target: dict[str, list[int]] = {}
    for index, relation in enumerate(relations):
        target = aliases.get(relation, relation)
        indexes_by_target.setdefault(target, []).append(index)

    groups = []
    for target, indexes in indexes_by_target.items():
        submitted_relation = target if len(indexes) > 1 else relations[indexes[0]]
        groups.append(
            RelationCheckGroup(
                relation=submitted_relation,
                indexes=tuple(indexes),
            )
        )
    return groups


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
