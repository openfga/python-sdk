import random
import uuid
import pytest

from datetime import datetime, timedelta


def random_datetime(
    min_year: int = 1900,
    max_year: int = datetime.now().year,
    min_date: datetime | None = None,
    max_date: datetime | None = None,
    iso_format: bool = True,
) -> str | datetime:
    """
    Generate a random datetime between `min_year` and `max_year`, or between `min_date` and `max_date`.

    Args:
        min_year (int): Minimum year for the datetime range (default is 1900).
        max_year (int): Maximum year for the datetime range (default is the current year).
        min_date (datetime | None): Optional minimum datetime value.
        max_date (datetime | None): Optional maximum datetime value.

    Returns:
        datetime: A random datetime within the specified range.

    Raises:
        ValueError: If `min_date` is greater than `max_date`.
    """
    if min_date and max_date and min_date > max_date:
        raise ValueError("`min_date` must be less than or equal to `max_date`.")

    if not min_date:
        min_date = datetime(min_year, 1, 1, 0, 0, 0)
    if not max_date:
        max_date = datetime(max_year, 12, 31, 23, 59, 59)

    total_seconds = int((max_date - min_date).total_seconds())

    random_seconds = random.randint(0, total_seconds)

    result = min_date + timedelta(seconds=random_seconds)

    if iso_format:
        return (
            f"{result.strftime('%Y-%m-%dT%H:%M:%S')}.{result.microsecond // 1000:03d}Z"
        )

    return result


def parse_iso_datetime(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")


@pytest.fixture
def mock_api_response_list_stores() -> list[dict[str, str | None]]:
    """
    Mock API response for list_stores endpoint.

    Returns:
        list[dict[str, str | None]]: A list of mocked store dictionaries.
    """

    def generate_store() -> dict[str, str | None]:
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
