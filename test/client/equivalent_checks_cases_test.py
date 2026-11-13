"""
Runs the shared equivalent-checks cases from openfga/language against the Python resolver.

The cases file is copied from openfga/language. Run `make update-equivalent-checks-cases`
to update it.
"""

import json

from pathlib import Path
from types import SimpleNamespace

import pytest

from openfga_sdk.client.equivalent_checks import resolve
from openfga_sdk.client.models.batch_check_item import ClientBatchCheckItem
from openfga_sdk.client.models.tuple import ClientTuple
from openfga_sdk.models.relationship_condition import RelationshipCondition
from openfga_sdk.sync.api_client import ApiClient


CASES_FILE = Path(__file__).parent.parent / "data" / "equivalent-checks-cases.json"
CASES = json.loads(CASES_FILE.read_text())["cases"]
MODEL_ID = "01GXSA8YR785C4FYS3C0RTG7B1"


def _model(model_json):
    with ApiClient() as api_client:
        return api_client.deserialize(
            SimpleNamespace(data=json.dumps(dict(model_json, id=MODEL_ID))),
            "AuthorizationModel",
        )


def _contextual_tuple(tuple_json):
    condition = tuple_json.get("condition")
    return ClientTuple(
        user=tuple_json["user"],
        relation=tuple_json["relation"],
        object=tuple_json["object"],
        condition=(
            RelationshipCondition(
                name=condition["name"], context=condition.get("context")
            )
            if condition is not None
            else None
        ),
    )


def _check(check_json):
    contextual_tuples = check_json.get("contextual_tuples")
    return ClientBatchCheckItem(
        user=check_json["user"],
        relation=check_json["relation"],
        object=check_json["object"],
        correlation_id=check_json["id"],
        context=check_json.get("context"),
        contextual_tuples=(
            [_contextual_tuple(item) for item in contextual_tuples]
            if contextual_tuples is not None
            else None
        ),
    )


def test_cases_file_is_not_empty():
    assert len(CASES) > 0


@pytest.mark.parametrize("case", CASES, ids=[case["name"] for case in CASES])
def test_equivalent_checks_case(case):
    checks = [_check(check) for check in case["checks"]]

    groups = resolve(_model(case["model"]), checks)

    actual = [
        {
            "id": group.check.correlation_id,
            "user": group.check.user,
            "relation": group.check.relation,
            "object": group.check.object,
            "for": [member.correlation_id for member in group.members],
        }
        for group in groups
    ]
    assert actual == case["expected_sent"]

    for group in groups:
        first = group.members[0]
        assert group.check.context is first.context
        assert group.check.contextual_tuples is first.contextual_tuples
