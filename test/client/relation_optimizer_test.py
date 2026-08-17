from openfga_sdk.client.relation_optimizer import (
    build_relation_aliases,
    group_relations,
    is_concrete_user,
)
from openfga_sdk.models.authorization_model import AuthorizationModel
from openfga_sdk.models.object_relation import ObjectRelation
from openfga_sdk.models.type_definition import TypeDefinition
from openfga_sdk.models.userset import Userset
from openfga_sdk.models.usersets import Usersets


def test_build_relation_aliases_only_includes_pure_aliases():
    model = AuthorizationModel(
        id="01GXSA8YR785C4FYS3C0RTG7B1",
        schema_version="1.1",
        type_definitions=[
            TypeDefinition(
                type="document",
                relations={
                    "can_comment": Userset(
                        computed_userset=ObjectRelation(relation="commenter")
                    ),
                    "can_reply": Userset(
                        computed_userset=ObjectRelation(relation="can_comment")
                    ),
                    "commenter": Userset(this={}),
                    "viewer": Userset(this={}),
                    "can_view": Userset(
                        union=Usersets(
                            child=[
                                Userset(
                                    computed_userset=ObjectRelation(relation="viewer")
                                )
                            ]
                        )
                    ),
                    "other_object": Userset(
                        computed_userset=ObjectRelation(
                            object="document:other", relation="viewer"
                        )
                    ),
                    "missing_target": Userset(
                        computed_userset=ObjectRelation(relation="missing")
                    ),
                    "cycle_a": Userset(
                        computed_userset=ObjectRelation(relation="cycle_b")
                    ),
                    "cycle_b": Userset(
                        computed_userset=ObjectRelation(relation="cycle_a")
                    ),
                },
            )
        ],
    )

    assert build_relation_aliases(model) == {
        "document": {
            "can_comment": "commenter",
            "can_reply": "commenter",
        }
    }


def test_group_relations_collapses_aliases_and_preserves_singletons():
    groups = group_relations(
        ["can_comment", "can_reply", "viewer", "commenter"],
        {
            "can_comment": "commenter",
            "can_reply": "commenter",
        },
    )

    assert [(group.relation, group.indexes) for group in groups] == [
        ("commenter", (0, 1, 3)),
        ("viewer", (2,)),
    ]


def test_is_concrete_user_rejects_usersets_and_wildcards():
    assert is_concrete_user("user:anne")
    assert not is_concrete_user("team:eng#member")
    assert not is_concrete_user("user:*")
    assert not is_concrete_user("*")
