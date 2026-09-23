"""Generalize quasi-identifiers and suppress groups that fail the checks."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .data import Record

MAX_LEVELS = (3, 3, 1)  # age, postal, sex
Chromosome = tuple[int, int, int]


@dataclass(frozen=True)
class Evaluation:
    genes: Chromosome
    generalization_cost: float
    suppression_rate: float
    retained: int
    groups: int
    constraint_violation: float

    @property
    def feasible(self) -> bool:
        return self.retained > 0 and self.constraint_violation <= 1e-12


def validate_genes(genes: Chromosome) -> None:
    if len(genes) != 3 or any(
        not isinstance(v, int) or isinstance(v, bool) or v < 0 or v > maximum
        for v, maximum in zip(genes, MAX_LEVELS)
    ):
        raise ValueError(f"genes must be integer levels within {MAX_LEVELS}")


def generalized_key(row: Record, genes: Chromosome) -> tuple[str, str, str]:
    validate_genes(genes)
    age_level, postal_level, sex_level = genes
    if not (18 <= row.age <= 89 and len(row.postal) == 5 and row.postal.isdigit()
            and row.sex in {"F", "M"} and row.diagnosis):
        raise ValueError("row outside the synthetic demonstration schema")

    if age_level == 0:
        age = str(row.age)
    elif age_level == 1:
        lo = (row.age // 10) * 10
        age = f"{lo}-{lo + 9}"
    elif age_level == 2:
        lo = (row.age // 20) * 20
        age = f"{lo}-{lo + 19}"
    else:
        age = "*"

    postal = (row.postal, row.postal[:3] + "**", row.postal[:1] + "****", "*****")[postal_level]
    sex = row.sex if sex_level == 0 else "*"
    return age, postal, sex


def anonymize(
    rows: list[Record], genes: Chromosome, k: int = 5, l: int = 2
) -> list[tuple[tuple[str, str, str], str]]:
    """Keep groups with at least k rows and l distinct diagnoses."""
    if k < 2 or l < 1 or l > k:
        raise ValueError("require k >= 2 and 1 <= l <= k")
    validate_genes(genes)
    groups: dict[tuple[str, str, str], list[Record]] = defaultdict(list)
    for row in rows:
        groups[generalized_key(row, genes)].append(row)

    output: list[tuple[tuple[str, str, str], str]] = []
    for key, members in groups.items():
        # Suppress the whole class; dropping only a few rows could break k.
        if len(members) >= k and len({r.diagnosis for r in members}) >= l:
            output.extend((key, r.diagnosis) for r in members)
    return output


def evaluate(
    rows: list[Record], genes: Chromosome, k: int = 5, l: int = 2,
    max_suppression: float = 0.30,
) -> Evaluation:
    if not rows or not 0 <= max_suppression < 1:
        raise ValueError("nonempty rows and 0 <= max_suppression < 1 required")
    result = anonymize(rows, genes, k=k, l=l)
    rate = (len(rows) - len(result)) / len(rows)
    # Use hierarchy depth as a simple cost; it does not measure clinical usefulness.
    cost = sum(level / maximum for level, maximum in zip(genes, MAX_LEVELS)) / 3
    violation = max(0.0, rate - max_suppression)
    if not result:
        violation += 1.0
    return Evaluation(genes, cost, rate, len(result), len({key for key, _ in result}), violation)


def check_output(output: list[tuple[tuple[str, str, str], str]], k: int, l: int) -> bool:
    """Check the rows that would actually be written to the CSV."""
    groups: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for key, diagnosis in output:
        groups[key].append(diagnosis)
    return bool(groups) and all(
        len(values) >= k and len(set(values)) >= l for values in groups.values()
    )
