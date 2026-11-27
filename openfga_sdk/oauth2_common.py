import math
import random

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class _TokenState:
    access_token: str
    expiry_time: datetime
    expiry_buffer: float


def jitter(loop_count, min_wait_in_ms):
    """
    Generate a random jitter value for exponential backoff
    """
    minimum = math.ceil(2**loop_count * min_wait_in_ms)
    maximum = math.ceil(2 ** (loop_count + 1) * min_wait_in_ms)
    # randrange() raises on an empty range, e.g. when min_wait_in_ms is 0
    if maximum <= minimum:
        return minimum / 1000
    return random.randrange(minimum, maximum) / 1000
