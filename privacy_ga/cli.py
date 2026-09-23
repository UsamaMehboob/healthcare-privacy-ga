"""Run the synthetic-data experiment."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict
from pathlib import Path

from .anonymize import anonymize, check_output, evaluate
from .data import synthetic_records
from .search import exhaustive_search, search


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=240, help="synthetic records")
    parser.add_argument("--data-seed", type=int, default=2026)
    parser.add_argument("--search-seed", type=int, default=7)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--l", type=int, default=2, help="distinct sensitive values")
    parser.add_argument("--max-suppression", type=float, default=0.30)
    parser.add_argument("--population", type=int, default=12)
    parser.add_argument("--generations", type=int, default=12)
    parser.add_argument("--out", type=Path, default=Path("results"))
    args = parser.parse_args(argv)

    rows = synthetic_records(args.n, args.data_seed)
    baseline = evaluate(rows, (3, 3, 1), args.k, args.l, args.max_suppression)
    found, evaluations = search(rows, args.k, args.l, args.max_suppression,
                                args.population, args.generations, args.search_seed)
    exact = exhaustive_search(rows, args.k, args.l, args.max_suppression)
    if not found:
        parser.error("no solution found within suppression budget; adjust settings")

    selected = min(found, key=lambda item: (item.generalization_cost, item.suppression_rate, item.genes))
    released = anonymize(rows, selected.genes, args.k, args.l)
    if not check_output(released, args.k, args.l):
        raise AssertionError("released data failed privacy invariant")

    args.out.mkdir(parents=True, exist_ok=True)
    report = {
        "description": "Synthetic data proof of concept; no patient data, real-world validation or clinical utility claim",
        "settings": {"n": args.n, "data_seed": args.data_seed,
                     "search_seed": args.search_seed, "k": args.k, "l": args.l,
                     "max_suppression": args.max_suppression,
                     "population": args.population, "generations": args.generations},
        "objectives": ["hierarchy-depth generalization cost (lower is better)",
                       "whole-row suppression rate (lower is better)"],
        "baseline_all_generalized": asdict(baseline),
        "selected": asdict(selected),
        "ga_pareto": [asdict(item) for item in found],
        "ga_policies_evaluated": evaluations,
        "possible_policies": 32,
        "exhaustive_reference_pareto": [asdict(item) for item in exact],
        "ga_found_exact_front": {item.genes for item in found} == {item.genes for item in exact},
        "released_invariant_verified": True,
    }
    (args.out / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    with (args.out / "synthetic_anonymized.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["age_generalized", "postal_generalized", "sex_generalized", "diagnosis"])
        for key, diagnosis in released:
            writer.writerow([*key, diagnosis])
    print(f"Synthetic records: {len(rows)}; released: {selected.retained}; groups: {selected.groups}")
    print(f"Selected genes (age, postal, sex): {selected.genes}")
    print(f"Generalization cost: {selected.generalization_cost:.4f}; suppression: {selected.suppression_rate:.4f}")
    print(f"GA matched exact Pareto set: {report['ga_found_exact_front']}")
    print(f"Policies evaluated by GA: {evaluations} of 32")
    print(f"Saved {args.out / 'report.json'} and {args.out / 'synthetic_anonymized.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
