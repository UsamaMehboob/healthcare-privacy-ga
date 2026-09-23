# Genetic algorithm for tabular data anonymization

This project tests a small part of a larger research idea: using a multi-objective genetic algorithm to choose how much to generalize or suppress records in a healthcare-style table. The example uses generated data. It is an experiment, not software for releasing patient records.

## Run it

You need Python 3.10 or later. There are no third-party runtime packages.

```bash
python -m privacy_ga.cli --out results
python -m unittest discover -s tests -v
```

The first command writes `results/report.json` and `results/synthetic_anonymized.csv`. The dataset is generated inside the program from a fixed seed. Run `python -m privacy_ga.cli --help` to change the seeds, dataset size, privacy thresholds, or search settings.

## How the experiment works

Each candidate policy has three numbers: `(age_level, postal_level, sex_level)`. They specify how to transform the quasi-identifiers:

| Field | Level 0 | Level 1 | Level 2 | Level 3 |
| --- | --- | --- | --- | --- |
| Age | Exact | 10-year interval | 20-year interval | `*` |
| Five-digit postal code | Exact | First 3 digits | First digit | `*****` |
| Sex | Exact | `*` | — | — |

There are 32 possible policies. For each one, the code groups records with the same transformed age, postal code, and sex. It suppresses a group if it has fewer than `k` records or fewer than `l` distinct diagnosis values. The defaults are `k=5` and `l=2`. Diagnosis stays in the output so the diversity check can be inspected.

The search tries to minimize **two separate costs**: the average depth of generalization across the three fields, and the fraction of records suppressed. It rejects candidates that exceed the suppression limit, which defaults to 30%. The evolutionary search uses nondominated sorting, crowding distance, tournament selection, crossover, and mutation. `search.py` also evaluates all 32 policies directly, so the report can check whether this particular GA run found the full Pareto set. Exhaustive evaluation is practical here because the example is small.

With the default settings (`n=240`, data seed `2026`, search seed `7`, population `12`, generations `12`), the run gives:

| Policy | Age, postal, sex levels | Generalization cost | Records suppressed |
| --- | --- | ---: | ---: |
| Fully generalized baseline | `(3, 3, 1)` | 1.0000 | 0 of 240 |
| Selected GA policy | `(1, 2, 0)` | 0.3333 | 46 of 240 |

The GA evaluated 29 of the 32 policies and found both policies on the exact Pareto front. The other one, `(3, 1, 0)`, has a generalization cost of 0.4444 and suppresses no records. The saved `examples/report.json` contains the complete default run; `examples/synthetic_anonymized.csv` contains its generated output.

