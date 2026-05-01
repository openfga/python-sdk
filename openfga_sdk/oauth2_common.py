import math
import random
import sys

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
    jitter = random.randrange(minimum, maximum) / 1000

    # If running in pytest, set jitter to 0 to speed up tests
    if "pytest" in sys.modules:
        jitter = 0

    return jitter
