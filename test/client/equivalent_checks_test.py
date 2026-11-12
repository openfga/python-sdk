import datetime
import math

import pytest

from openfga_sdk.client.equivalent_checks import (
    EquivalentCheckGroup,
    expand,
    merge_enabled,
    resolve,
    unmerged,
    validate_correlation_ids,
)
from openfga_sdk.client.models.batch_check_item import ClientBatchCheckItem
from openfga_sdk.client.models.tuple import ClientTuple
from openfga_sdk.exceptions import FgaValidationException
from openfga_sdk.models.authorization_model import AuthorizationModel
from openfga_sdk.models.batch_check_single_result import BatchCheckSingleResult
from openfga_sdk.models.check_error import CheckError
from openfga_sdk.models.object_relation import ObjectRelation
from openfga_sdk.models.relationship_condition import RelationshipCondition
from openfga_sdk.models.type_definition import TypeDefinition
from openfga_sdk.models.userset import Userset


# define viewer: [user], can_view: viewer
MODEL = AuthorizationModel(
    id="01GXSA8YR785C4FYS3C0RTG7B1",
    schema_version="1.1",
    type_definitions=[
        TypeDefinition(type="user"),
        TypeDefinition(
            type="document",
            relations={
                "viewer": Userset(this={}),
                "can_view": Userset(
                    computed_userset=ObjectRelation(object="", relation="viewer")
                ),
            },
        ),
    ],
)


def check(correlation_id, relation="can_view", context=None, contextual_tuples=None):
    return ClientBatchCheckItem(
        user="user:anne",
        relation=relation,
        object="document:1",
        correlation_id=correlation_id,
        context=context,
        contextual_tuples=contextual_tuples,
    )


def sent(groups):
    return [
        (
            group.check.correlation_id,
            group.check.relation,
            [member.correlation_id for member in group.members],
        )
        for group in groups
    ]


@pytest.mark.parametrize(
    "value",
    [
        math.nan,
        math.inf,
        10**400,
        (1, 2),
        datetime.datetime(2026, 1, 1),
        {1: "non-string key"},
        {"nested": [object()]},
    ],
    ids=["nan", "inf", "huge-int", "tuple", "datetime", "int-key", "object"],
)
def test_values_that_cannot_be_compared_are_sent_as_is(value):
    groups = resolve(
        MODEL,
        [check("a", context={"x": value}), check("b", context={"x": value})],
    )

    assert sent(groups) == [("a", "can_view", ["a"]), ("b", "can_view", ["b"])]


def test_a_context_that_is_not_an_object_is_sent_as_is():
    groups = resolve(MODEL, [check("a", context=["x"]), check("b", context=["x"])])

    assert sent(groups) == [("a", "can_view", ["a"]), ("b", "can_view", ["b"])]


def test_values_in_a_condition_context_that_cannot_be_compared_are_sent_as_is():
    contextual_tuples = [
        ClientTuple(
            user="user:anne",
            relation="viewer",
            object="document:2",
            condition=RelationshipCondition(name="c", context={"x": math.nan}),
        )
    ]

    groups = resolve(
        MODEL,
        [
            check("a", contextual_tuples=contextual_tuples),
            check("b", contextual_tuples=contextual_tuples),
        ],
    )

    assert sent(groups) == [("a", "can_view", ["a"]), ("b", "can_view", ["b"])]


def test_checks_that_are_not_strings_are_sent_as_is():
    item = check("a")
    item.user = None

    assert sent(resolve(MODEL, [item])) == [("a", "can_view", ["a"])]


def test_a_model_without_type_definitions_sends_everything_as_is():
    model = AuthorizationModel(
        id="01GXSA8YR785C4FYS3C0RTG7B1", schema_version="1.1", type_definitions=[]
    )

    assert sent(resolve(model, [check("a"), check("b")])) == [
        ("a", "can_view", ["a"]),
        ("b", "can_view", ["b"]),
    ]


def test_unmerged_sends_every_check_as_is():
    items = [check("a"), check("b")]

    assert sent(unmerged(items)) == [
        ("a", "can_view", ["a"]),
        ("b", "can_view", ["b"]),
    ]


@pytest.mark.parametrize(
    "correlation_id",
    ["", "has space", "x" * 37, "é", "a/b", "a\n", 1],
)
def test_validate_correlation_ids_rejects_invalid_ids(correlation_id):
    with pytest.raises(FgaValidationException, match="is invalid"):
        validate_correlation_ids([check(correlation_id)])


@pytest.mark.parametrize(
    "options, enabled",
    [
        (None, False),
        ({}, False),
        ({"merge_equivalent_checks": None}, False),
        ({"merge_equivalent_checks": False}, False),
        ({"merge_equivalent_checks": True}, True),
    ],
)
def test_merge_enabled(options, enabled):
    assert merge_enabled(options) is enabled


@pytest.mark.parametrize("value", ["true", 1, "yes"])
def test_merge_enabled_rejects_values_that_are_not_bools(value):
    with pytest.raises(
        FgaValidationException, match="merge_equivalent_checks must be a bool"
    ):
        merge_enabled({"merge_equivalent_checks": value})


def test_validate_correlation_ids_accepts_valid_ids():
    validate_correlation_ids([check("a_b-1"), check("x" * 36)])


def test_validate_correlation_ids_rejects_duplicates():
    with pytest.raises(
        FgaValidationException, match=r"Duplicate correlation_id \(a\) provided"
    ):
        validate_correlation_ids([check("a"), check("a")])


def test_expand_copies_answers_in_input_order():
    a, b, c = check("a"), check("b"), check("c", relation="viewer")
    groups = [
        EquivalentCheckGroup(check=check("c", relation="viewer"), members=[c]),
        EquivalentCheckGroup(
            check=check("merged-1", relation="viewer"), members=[a, b]
        ),
    ]
    error = CheckError(message="boom")

    responses = expand(
        [a, b, c],
        groups,
        {
            "merged-1": BatchCheckSingleResult(error=error),
            "c": BatchCheckSingleResult(allowed=True),
            "unknown": BatchCheckSingleResult(allowed=True),
        },
    )

    assert [(r.correlation_id, r.allowed, r.error) for r in responses] == [
        ("a", False, error),
        ("b", False, error),
        ("c", True, None),
    ]
    assert [r.request for r in responses] == [a, b, c]


def test_expand_turns_a_missing_answer_into_an_error():
    a, b = check("a"), check("b")

    responses = expand(
        [a, b],
        [EquivalentCheckGroup(check=check("merged-1"), members=[a, b])],
        {},
    )

    for response in responses:
        assert response.allowed is False
        assert response.error.message == (
            "No result returned for correlation_id (merged-1)"
        )


@pytest.mark.parametrize(
    "can_view",
    [
        Userset(computed_userset=ObjectRelation(object="parent", relation="viewer")),
        Userset(this={}, computed_userset=ObjectRelation(object="", relation="viewer")),
    ],
    ids=["object-set", "mixed-rewrite"],
)
def test_rewrites_that_only_look_like_aliases_are_not_merged(can_view):
    model = AuthorizationModel(
        id="01GXSA8YR785C4FYS3C0RTG7B1",
        schema_version="1.1",
        type_definitions=[
            TypeDefinition(type="user"),
            TypeDefinition(
                type="document",
                relations={"viewer": Userset(this={}), "can_view": can_view},
            ),
        ],
    )

    groups = resolve(model, [check("a", relation="viewer"), check("b")])

    assert sent(groups) == [("a", "viewer", ["a"]), ("b", "can_view", ["b"])]
