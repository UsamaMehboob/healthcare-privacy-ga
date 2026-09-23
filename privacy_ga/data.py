"""Generate records for the example experiment."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random


@dataclass(frozen=True)
class Record:
    age: int
    postal: str
    sex: str
    diagnosis: str


def synthetic_records(n: int = 240, seed: int = 2026) -> list[Record]:
    """Generate the same artificial records for a given seed."""
    if n < 1:
        raise ValueError("n must be positive")
    rng = Random(seed)
    prefixes = ("100", "101", "200", "201", "300", "301")
    diagnoses = ("respiratory", "cardiovascular", "metabolic", "other")
    return [
        Record(
            age=rng.randint(18, 89),
            postal=rng.choice(prefixes) + f"{rng.randrange(100):02d}",
            sex=rng.choice(("F", "M")),
            diagnosis=rng.choice(diagnoses),
        )
        for _ in range(n)
    ]
