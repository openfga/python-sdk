from typing import Any, TypeVar

from openfga_sdk.client.models.batch_check_item import ClientBatchCheckItem
from openfga_sdk.client.models.batch_check_request import ClientBatchCheckRequest
from openfga_sdk.client.models.tuple import ClientTuple
from openfga_sdk.client.models.write_request import ClientWriteRequest


Request = TypeVar("Request")


def parse_request(body: Request | dict[str, Any], model: type[Request]) -> Request:
    """Construct a request from constructor arguments without changing the input."""
    if not isinstance(body, dict):
        return body

    fields = dict(body)
    nested_lists: dict[str, type[Any]] = {"contextual_tuples": ClientTuple}
    if model is ClientWriteRequest:
        nested_lists.update(writes=ClientTuple, deletes=ClientTuple)
    elif model is ClientBatchCheckRequest:
        nested_lists["checks"] = ClientBatchCheckItem

    for field, nested_model in nested_lists.items():
        if fields.get(field) is not None:
            fields[field] = [
                parse_request(item, nested_model) for item in fields[field]
            ]

    return model(**fields)
