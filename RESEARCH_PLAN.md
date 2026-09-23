# Research notes

The code in this repository is a small experiment using artificial records. This document records questions to investigate if the work continues; it does not report completed studies.

## Main question

Can a genetic algorithm find generalization and suppression policies that meet defined privacy constraints without losing information needed for a particular health analysis?

## Starting point

The current experiment has 32 global policies and two costs: generalization depth and row suppression. It checks group size and the number of distinct diagnosis values in each retained group. It can compare a GA run against all 32 policies, but it cannot measure whether a medical analysis remains accurate. The generated fields and diagnoses are independent by construction.

## Questions for future experiments

1. Add more quasi-identifiers and defensible generalization hierarchies. Compare the GA with random search and other baselines as the number of policies grows. Use exhaustive search only while it remains practical.
2. Pick an analysis before transforming the data. Compare its results before and after anonymization, including differences across relevant subgroups. Any real data would require appropriate access and disclosure review first.
3. Evaluate linkage and attribute-disclosure risks. Explore t-closeness and, for suitable aggregate releases, differential privacy with proper privacy accounting. These would be separate implementations and evaluations.
4. Repeat experiments with multiple seeds. Publish the configurations, run times, objective values, and uncertainty instead of reporting one favorable run.

## What to report

For each run, record both costs, the number of retained records, the group checks on output rows, the number of policies evaluated, and agreement with an exact reference when available. Results on generated data would show only how the algorithm behaves on that generated data.
