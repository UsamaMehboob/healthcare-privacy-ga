import unittest

from privacy_ga.anonymize import anonymize, check_output, evaluate
from privacy_ga.data import Record, synthetic_records
from privacy_ga.search import exhaustive_search, search


class PrototypeTests(unittest.TestCase):
    def test_synthetic_reproducibility(self):
        self.assertEqual(synthetic_records(25, 9), synthetic_records(25, 9))
        self.assertNotEqual(synthetic_records(25, 9), synthetic_records(25, 10))

    def test_release_suppresses_small_or_homogeneous_classes(self):
        rows = [
            Record(25, "10001", "F", "A"), Record(25, "10001", "F", "B"),
            Record(40, "20001", "M", "A"), Record(40, "20001", "M", "A"),
            Record(70, "30001", "F", "B"),
        ]
        released = anonymize(rows, (0, 0, 0), k=2, l=2)
        self.assertEqual(len(released), 2)
        self.assertTrue(check_output(released, 2, 2))

    def test_all_suppressed_is_infeasible(self):
        rows = [Record(23, "10001", "F", "A"), Record(23, "10001", "F", "A")]
        score = evaluate(rows, (0, 0, 0), k=2, l=2)
        self.assertFalse(score.feasible)
        self.assertFalse(check_output([], 2, 2))

    def test_search_privacy_and_exact_reference(self):
        rows = synthetic_records(160, 2026)
        ga, evaluated = search(rows, population_size=12, generations=12, seed=3)
        exact = exhaustive_search(rows)
        self.assertTrue(ga)
        self.assertLessEqual(evaluated, 32)
        for result in ga:
            self.assertTrue(result.feasible)
            self.assertTrue(check_output(anonymize(rows, result.genes), 5, 2))
            self.assertIn(result.genes, {candidate.genes for candidate in exact})


if __name__ == "__main__":
    unittest.main()
