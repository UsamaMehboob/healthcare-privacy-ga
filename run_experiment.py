"""
Run 60 experiments (20 seeds x 3 sizes) 
"""
from statistics import median

from privacy_ga.anonymize import evaluate
from privacy_ga.data import synthetic_records
from privacy_ga.search import exhaustive_search, search


def run_one(rows, data_seed, search_seed):
    data = synthetic_records(rows, data_seed)
    ga, evaluated = search(
        data, k=5, l=2, max_suppression=0.30,
        population_size=12, generations=12, seed=search_seed,
    )
    exact = exhaustive_search(data, k=5, l=2, max_suppression=0.30)
    match = {e.genes for e in ga} == {e.genes for e in exact}
    if ga:
        sel = min(ga, key=lambda item: (item.generalization_cost, item.suppression_rate, item.genes))
        H, S = sel.generalization_cost, sel.suppression_rate
    else:
        H = S = float("nan")
    return match, evaluated, H, S


def main():
    print(f"{'rows':>5} {'data_seed':>10} {'search_seed':>12} {'match':>6} {'eval':>5} "
          f"{'H':>8} {'S':>8}")
    all_rows = {}
    for n in (160, 240, 480):
        rows_summary = []
        for i in range(20):
            data_seed, search_seed = 2026 + i, 7 + i
            m, e, H, S = run_one(n, data_seed, search_seed)
            rows_summary.append((m, e, H, S))
            print(f"{n:>5} {data_seed:>10} {search_seed:>12} {str(m):>6} {e:>5} "
                  f"{H:>8.4f} {S:>8.4f}")
        all_rows[n] = rows_summary
    print("\n=== Summary (Table 1) ===")
    print(f"{'Rows':>5} {'Exact matches':>15} {'Median eval':>13} {'Eval range':>12} "
          f"{'Median H':>10} {'Median S':>10}")
    for n, rows_summary in all_rows.items():
        matches = sum(1 for r in rows_summary if r[0])
        evals = [r[1] for r in rows_summary]
        Hs = [r[2] for r in rows_summary]
        Ss = [r[3] for r in rows_summary]
        print(f"{n:>5} {str(matches) + '/20':>15} {median(evals):>13.0f} "
              f"{str(min(evals)) + '-' + str(max(evals)):>12} "
              f"{median(Hs):>10.4f} {median(Ss):>10.4f}")


if __name__ == "__main__":
    main()