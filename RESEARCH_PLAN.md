# Research Plan and Progress

My research plan is to continue researching the use of multi-objective genetic algorithms for healthcare data anonymization, with the goal of protecting sensitive patient information while preserving sufficient data utility for healthcare research and analysis.

## Current Progress

As an initial step toward this research, I have conducted an experimental study employing a genetic algorithm on synthetic healthcare-style records. This study evaluates anonymization policies based on different levels of generalization and suppression while applying privacy constraints including k-anonymity and l-diversity.

Initially, the search space was purposefully kept smaller (limited to 32 possible policies) so that the genetic algorithm could be compared against exhaustive search easily, and to establish the comparative reference for later iterations. The source code, experimental scripts, and results have also been made publicly available through GitHub to allow the work to be reproduced and further developed.

## Planned Research

### Expand the anonymization search space.

The current study uses a 32-policy space for verifiability as initial baseline. I plan to scale this to larger search space with additional quasi-identifiers, and deeper generalization depth for each identifier. This will yield search spaces with thousands of candidate policies and would serve as meaningful test of whether genetic search can identify strong anonymization policies ( within suppression and utility constraints ) while evaluating only a fraction of the available search space. This will also let us quantify the computational advantage of the GA-based method over traditional searches on realistic healthcare data.

### Extend the privacy requirements.

The current implementation uses k-anonymity and distinct l-diversity. Future work will investigate stronger privacy requirements, including differential privacy and t-closeness to further safeguard against re-identification threats. Re-identification risk becomes a more serious challenge as the search space grows, and these stronger constraints will create optimization problems that better reflect real-world healthcare records.

### Evaluate larger-scale and appropriately governed healthcare data.

After validating the approach on more realistic synthetic datasets, I intend to apply the GA-based search to real-world federated healthcare data networks such as PCORnet, the FDA Sentinel Initiative, and the NIH All of Us Research Program. These are active U.S. research networks involving millions of patient records contributed by Americans, and privacy-preserving analytics is a recognized ongoing challenge in each of them.

## Publishing Online framework

Current work toward this research is hosted publicly under the MIT license at [https://github.com/UsamaMehboob/healthcare-privacy-ga](https://github.com/UsamaMehboob/healthcare-privacy-ga). As the framework matures through the phases above, I intend to package it as a one-stop toolkit with plug-and-play features that researchers using healthcare data networks like PCORnet, FDA Sentinel can deploy directly. My professional DevOps background in building data automation pipelines will help make this genuinely deployable in the systems that host research data.

## Summary

My research plan builds on the genetic algorithm foundation described in my [prior publication](https://dl.acm.org/doi/10.1007/s00500-016-2070-9) and on my recent manuscript documenting an experimental study using a multi-objective genetic algorithm for anonymization on synthetic tabular health data ([https://www.preprints.org/manuscript/202609.2305](https://www.preprints.org/manuscript/202609.2305) ). The source code and this manuscript are both publicly available to serve as a documented evidence of active research.