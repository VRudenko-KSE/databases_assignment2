"""Fixed assignment data profiles and report parameters."""

from dataclasses import dataclass
from typing import Literal

Profile = Literal["default", "reduced"]
Operation = Literal["R1", "R2", "R3", "R4", "INSERT"]

TIMEZONE = "UTC"
STATION_COUNT = 32
HISTORICAL_START = "2026-01-01 00:00:00+00"
HISTORICAL_END = "2026-06-30 00:00:00+00"


@dataclass(frozen=True)
class ProfileSpec:
    name: Profile
    event_count: int
    device_count: int
    batch_count: int


def profile_spec(name: Profile) -> ProfileSpec:
    if name == "default":
        return ProfileSpec("default", 1_000_000, 20_000, 10_000)
    if name == "reduced":
        return ProfileSpec("reduced", 100_000, 2_000, 1_000)
    raise ValueError("profile must be default or reduced")


def report_parameters(operation: Operation) -> dict[str, str | int]:
    """Return a fresh mapping; every interval has an exclusive end."""
    if operation == "R1":
        return {"timezone": TIMEZONE, "device_id": 42, "limit": 20}
    if operation == "R2":
        return {"timezone": TIMEZONE, "station_id": 7,
                "start": "2026-03-01 00:00:00+00", "end": "2026-03-08 00:00:00+00"}
    if operation == "R3":
        return {"timezone": TIMEZONE, "station_count": STATION_COUNT, "expected_rows": 992,
                "start": "2026-03-01 00:00:00+00", "end": "2026-04-01 00:00:00+00"}
    if operation == "R4":
        return {"timezone": TIMEZONE, "station_count": STATION_COUNT, "expected_rows": 5_760,
                "start": HISTORICAL_START, "end": HISTORICAL_END}
    if operation == "INSERT":
        return {"timezone": TIMEZONE, "source": "mobility.ingest_batch",
                "target": "a2_write.events", "order_by": "event_id"}
    raise ValueError("operation must be R1, R2, R3, R4, or INSERT")
