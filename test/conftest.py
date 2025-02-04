import random
import uuid

from datetime import datetime, timedelta
from typing import Literal

import pytest


def random_datetime_obj(
    min_year: int = 1900,
    max_year: int = datetime.now().year,
    min_date: datetime | None = None,
    max_date: datetime | None = None,
) -> datetime:
    if min_date and max_date and min_date > max_date:
        raise ValueError("`min_date` must be less than or equal to `max_date`.")

    if not min_date:
        min_date = datetime(min_year, 1, 1, 0, 0, 0)
    if not max_date:
        max_date = datetime(max_year, 12, 31, 23, 59, 59)

    total_seconds = int((max_date - min_date).total_seconds())

    random_seconds = random.randint(0, total_seconds)

    return min_date + timedelta(seconds=random_seconds)


def random_datetime(
    min_year: int = 1900,
    max_year: int = datetime.now().year,
    min_date: datetime | None = None,
    max_date: datetime | None = None,
) -> str:
    result = random_datetime_obj(min_year, max_year, min_date, max_date)
    return f"{result.strftime('%Y-%m-%dT%H:%M:%S')}.{result.microsecond // 1000:03d}Z"


def parse_iso_datetime(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")


@pytest.fixture
def mock_api_response_list_stores() -> list[
    dict[
        Literal["id", "name", "created_at", "updated_at", "deleted_at"],
        str | datetime | None,
    ]
]:
    """
    Mock API response for list_stores endpoint.

    Returns:
        list[dict[Literal["id", "name", "created_at", "updated_at", "deleted_at"], str | datetime | None]]: A list of mocked store responses.
    """

    def generate_store() -> dict[
        Literal["id", "name", "created_at", "updated_at", "deleted_at"],
        str | datetime | None,
    ]:
        """Generate a single mock store."""
        return {
            "id": str(uuid.uuid4()),
            "name": f"Store {random.randint(1, 1000)}",
            "created_at": random_datetime(),
            "updated_at": random_datetime(),
            "deleted_at": (random_datetime() if random.random() > 0.7 else None),
        }

    num_stores = random.randint(1, 10)
    return [generate_store() for _ in range(num_stores)]


@pytest.fixture
def mock_api_response_create_store() -> dict[
    Literal["id", "name", "created_at", "updated_at"], str | datetime
]:
    """
    Mock API response for create_store endpoint.

    Returns:
        dict[Literal["id", "name", "created_at", "updated_at"], str | datetime]: A mocked store response.
    """

    return {
        "id": str(uuid.uuid4()),
        "name": f"Store {random.randint(1, 1000)}",
        "created_at": random_datetime(),
        "updated_at": random_datetime(),
    }


@pytest.fixture
def mock_api_response_get_store() -> dict[
    Literal["id", "name", "created_at", "updated_at"], str | datetime
]:
    """
    Mock API response for get_store endpoint.

    Returns:
        dict[Literal["id", "name", "created_at", "updated_at"], str | datetime]: A mocked store response.
    """

    return {
        "id": str(uuid.uuid4()),
        "name": f"Store {random.randint(1, 1000)}",
        "created_at": random_datetime(),
        "updated_at": random_datetime(),
        "deleted_at": (random_datetime() if random.random() > 0.7 else None),
    }


@pytest.fixture
def mock_api_response_read_authorization_model() -> dict[
    Literal["conditions", "id", "schema_version", "type_definitions"], str | None
]:
    """
    Mock API response for read_authorization_model endpoint.

    Returns:
        dict[Literal["conditions", "id", "schema_version", "type_definitions"], str | None]: A mocked model response.
    """

    return {
        "conditions": None,
        "id": str(uuid.uuid4()),
        "schema_version": "1.0",
        "type_definitions": None,
    }


@pytest.fixture
def mock_api_response_read_authorization_models() -> list[
    dict[Literal["conditions", "id", "schema_version", "type_definitions"], str | None]
]:
    """
    Mock API response for read_authorization_models endpoint.

    Returns:
        list[dict[Literal["conditions", "id", "schema_version", "type_definitions"], str | None]]: A list of mocked model responses.
    """

    def generate_model() -> dict[
        Literal["conditions", "id", "schema_version", "type_definitions"], str | None
    ]:
        return {
            "conditions": None,
            "id": str(uuid.uuid4()),
            "schema_version": "1.0",
            "type_definitions": None,
        }

    num_models = random.randint(1, 10)
    return [generate_model() for _ in range(num_models)]


@pytest.fixture
def mock_api_response_write_authorization_model() -> dict[
    Literal["authorization_model_id"], str
]:
    """
    Mock API response for write_authorization_model endpoint.

    Returns:
        dict[Literal["authorization_model_id"], str]: A mocked response with authorization model ID.
    """

    return {
        "authorization_model_id": str(uuid.uuid4()),
    }


@pytest.fixture
def mock_api_response_read_changes() -> list[
    dict[
        Literal["timestamp", "tuple_key", "operation"],
        str
        | datetime
        | dict[Literal["object", "relation", "user", "conditions"], str | None],
    ]
]:
    """
    Mock API response for read_changes endpoint.

    Returns:
        list[dict[Literal["timestamp", "tuple_key", "operation"], str | datetime | dict[Literal["object", "relation", "user", "conditions"], str | None]]]: A list of mocked changes.
    """

    def generate_change() -> dict[
        Literal["timestamp", "tuple_key", "operation"],
        str
        | datetime
        | dict[Literal["object", "relation", "user", "conditions"], str | None],
    ]:
        return {
            "tuple_key": {
                "object": f"object_{random.randint(1, 1000)}",
                "relation": f"relation_{random.randint(1, 1000)}",
                "user": f"user_{random.randint(1, 1000)}",
                "condition": None,
            },
            "operation": random.choice(
                ["TUPLE_OPERATION_WRITE", "TUPLE_OPERATION_DELETE"]
            ),
            "timestamp": random_datetime(),
        }

    num_changes = random.randint(1, 10)
    return [generate_change() for _ in range(num_changes)]


@pytest.fixture
def mock_api_response_read() -> list[
    dict[
        Literal["timestamp", "tuple_key"],
        str | datetime | dict[Literal["object", "relation", "user"], str],
    ]
]:
    """
    Mock API response for read endpoint.

    Returns:
        list[dict[Literal["timestamp", "tuple_key"], str | datetime | dict[Literal["object", "relation", "user"], str]]]: A list of mocked results.
    """

    def generate_change() -> dict[
        Literal["timestamp", "tuple_key"],
        str | datetime | dict[Literal["object", "relation", "user"], str],
    ]:
        return {
            "key": {
                "object": f"object_{random.randint(1, 1000)}",
                "relation": f"relation_{random.randint(1, 1000)}",
                "user": f"user_{random.randint(1, 1000)}",
                "condition": None,
            },
            "timestamp": random_datetime(),
        }

    num_changes = random.randint(1, 10)
    return [generate_change() for _ in range(num_changes)]
