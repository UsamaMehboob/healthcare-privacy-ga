
    
  
"""Search over generalization policies."""

from __future__ import annotations

from itertools import product
from random import Random

from .anonymize import MAX_LEVELS, Chromosome, Evaluation, evaluate
from .data import Record


def dominates(a: Evaluation, b: Evaluation) -> bool:
    if a.feasible != b.feasible:
        return a.feasible

    if not a.feasible:
        return a.constraint_violation < b.constraint_violation

    a_costs = (a.generalization_cost, a.suppression_rate)
    b_costs = (b.generalization_cost, b.suppression_rate)
    return (
        all(x <= y for x, y in zip(a_costs, b_costs))
        and any(x < y for x, y in zip(a_costs, b_costs))
    )


def fronts(population: list[Evaluation]) -> list[list[Evaluation]]:
    """Group policies by nondomination rank."""
    beaten: list[list[int]] = [[] for _ in population]
    counts = [0] * len(population)
    layers: list[list[int]] = [[]]

    for i, a in enumerate(population):
        for j, b in enumerate(population):
            if i == j:
                continue
            if dominates(a, b):
                beaten[i].append(j)
            elif dominates(b, a):
                counts[i] += 1

        if counts[i] == 0:
            layers[0].append(i)

    index = 0
    while layers[index]:
        next_layer = []
        for i in layers[index]:
            for j in beaten[i]:
                counts[j] -= 1
                if counts[j] == 0:
                    next_layer.append(j)

        layers.append(next_layer)
        index += 1

    return [[population[i] for i in layer] for layer in layers if layer]


def crowding(layer: list[Evaluation]) -> dict[Chromosome, float]:
    distances = {item.genes: 0.0 for item in layer}
    if len(layer) <= 2:
        return {item.genes: float("inf") for item in layer}

    for objective in ("generalization_cost", "suppression_rate"):
        ranked = sorted(
            layer,
            key=lambda item: (getattr(item, objective), item.genes),
        )
        distances[ranked[0].genes] = float("inf")
        distances[ranked[-1].genes] = float("inf")

        span = getattr(ranked[-1], objective) - getattr(ranked[0], objective)
        if span == 0:
            continue

        for i in range(1, len(ranked) - 1):
            gap = (
                getattr(ranked[i + 1], objective)
                - getattr(ranked[i - 1], objective)
            )
            distances[ranked[i].genes] += gap / span

    return distances


def _front_sort_key(item: Evaluation) -> tuple[float, float, Chromosome]:
    return item.suppression_rate, item.generalization_cost, item.genes


def search(
    rows: list[Record],
    k: int = 5,
    l: int = 2,
    max_suppression: float = 0.30,
    population_size: int = 12,

