from openfga_sdk.client.models.batch_check_item import ClientBatchCheckItem
from openfga_sdk.client.models.tuple import ClientTuple
from openfga_sdk.client.relation_optimizer import (
    build_relation_aliases,
    group_batch_checks,
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
                    "mixed_rewrite": Userset(
                        computed_userset=ObjectRelation(relation="viewer"),
                        union=Usersets(child=[Userset(this={})]),
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


def test_group_batch_checks_requires_all_non_relation_inputs_to_match():
    contextual_tuple = ClientTuple(
        user="user:bob",
        relation="viewer",
        object="document:roadmap",
    )
    matching = {
        "user": "user:anne",
        "object": "document:roadmap",
        "context": {"view_count": 1},
        "contextual_tuples": [contextual_tuple],
    }
    checks = [
        ClientBatchCheckItem(relation="can_comment", **matching),
        ClientBatchCheckItem(
            relation="can_reply",
            **{
                **matching,
                "contextual_tuples": [
                    ClientTuple(
                        user="user:bob",
                        relation="viewer",
                        object="document:roadmap",
                    )
                ],
            },
        ),
        ClientBatchCheckItem(relation="commenter", **matching),
        ClientBatchCheckItem(
            user="user:bob",
            relation="can_comment",
            object="document:roadmap",
            context={"view_count": 1},
            contextual_tuples=[contextual_tuple],
        ),
        ClientBatchCheckItem(
            user="user:anne",
            relation="can_reply",
            object="document:roadmap",
            context={"view_count": 2},
            contextual_tuples=[contextual_tuple],
        ),
        ClientBatchCheckItem(
            user="user:anne",
            relation="can_comment",
            object="document:roadmap",
            context={"view_count": 1},
            contextual_tuples=[],
        ),
        ClientBatchCheckItem(
            user="user:anne", relation="viewer", object="document:roadmap"
        ),
        ClientBatchCheckItem(
            user="user:anne", relation="viewer", object="document:roadmap"
        ),
        ClientBatchCheckItem(
            user="user:anne", relation="can_comment", object="document"
        ),
    ]

    groups = group_batch_checks(
        checks,
        {
            "document": {
                "can_comment": "commenter",
                "can_reply": "commenter",
            }
        },
    )

    assert [(group.relation, group.indexes) for group in groups] == [
        ("commenter", (0, 1, 2)),
        ("can_comment", (3,)),
        ("can_reply", (4,)),
        ("can_comment", (5,)),
        ("viewer", (6,)),
        ("viewer", (7,)),
        ("can_comment", (8,)),
    ]
