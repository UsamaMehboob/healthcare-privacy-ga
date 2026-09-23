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
    x = (a.generalization_cost, a.suppression_rate)
    y = (b.generalization_cost, b.suppression_rate)
    return all(u <= v for u, v in zip(x, y)) and any(u < v for u, v in zip(x, y))


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
        ranked = sorted(layer, key=lambda item: (getattr(item, objective), item.genes))
        distances[ranked[0].genes] = float("inf")
        distances[ranked[-1].genes] = float("inf")
        span = getattr(ranked[-1], objective) - getattr(ranked[0], objective)
        if span:
            for i in range(1, len(ranked) - 1):
                distances[ranked[i].genes] += (
                    getattr(ranked[i + 1], objective) - getattr(ranked[i - 1], objective)
                ) / span
    return distances


def search(
    rows: list[Record], k: int = 5, l: int = 2, max_suppression: float = 0.30,
    population_size: int = 12, generations: int = 12, seed: int = 7,
) -> tuple[list[Evaluation], int]:
    """Return the policies found on the Pareto front and the evaluation count."""
    possible = 1
    for maximum in MAX_LEVELS:
        possible *= maximum + 1
    if not 4 <= population_size < possible or generations < 1:
        raise ValueError(f"require 4 <= population_size < {possible} and generations >= 1")
    rng = Random(seed)
    cache: dict[Chromosome, Evaluation] = {}

    def score(genes: Chromosome) -> Evaluation:
        if genes not in cache:
            cache[genes] = evaluate(rows, genes, k, l, max_suppression)
        return cache[genes]

    def sample() -> Chromosome:
        return (rng.randint(0, MAX_LEVELS[0]),
                rng.randint(0, MAX_LEVELS[1]),
                rng.randint(0, MAX_LEVELS[2]))

    # Include both ends of the hierarchy, then fill with distinct random policies.
    initial = {(3, 3, 1): score((3, 3, 1)), (0, 0, 0): score((0, 0, 0))}
    while len(initial) < population_size:
        candidate = score(sample())
        initial[candidate.genes] = candidate
    population = list(initial.values())

    for _ in range(generations):
        layers = fronts(population)
        ranks = {item.genes: i for i, layer in enumerate(layers) for item in layer}
        distances = {g: d for layer in layers for g, d in crowding(layer).items()}

        def tournament() -> Evaluation:
            a, b = rng.sample(population, 2)
            return min((a, b), key=lambda item: (ranks[item.genes], -distances[item.genes], item.genes))

        offspring = []
        for _ in range(population_size):
            a, b = tournament(), tournament()
            child = [rng.choice((x, y)) for x, y in zip(a.genes, b.genes)]
            for i, maximum in enumerate(MAX_LEVELS):
                if rng.random() < 0.25:
                    child[i] = rng.randint(0, maximum)
            offspring.append(score((child[0], child[1], child[2])))

        # Clones should not displace distinct policies in the next generation.
        combined = {item.genes: item for item in population + offspring}
        population = []
        for layer in fronts(list(combined.values())):
            if len(population) + len(layer) <= population_size:
                population.extend(layer)
            else:
                distance = crowding(layer)
                population.extend(sorted(layer, key=lambda v: (-distance[v.genes], v.genes))[:population_size - len(population)])
                break

    feasible = [item for item in cache.values() if item.feasible]
    if not feasible:
        return [], len(cache)
    pareto = fronts(feasible)[0]
    return sorted(set(pareto), key=lambda item: (item.suppression_rate, item.generalization_cost, item.genes)), len(cache)


def exhaustive_search(
    rows: list[Record], k: int = 5, l: int = 2, max_suppression: float = 0.30,
) -> list[Evaluation]:
    """Check all policies in this small search space."""
    all_scores = [
        evaluate(rows, genes, k, l, max_suppression)
        for genes in product(*(range(maximum + 1) for maximum in MAX_LEVELS))
    ]
    feasible = [item for item in all_scores if item.feasible]
    if not feasible:
        return []
    return sorted(fronts(feasible)[0], key=lambda item: (item.suppression_rate, item.generalization_cost, item.genes))
