import unittest

from services.topic_distribution import (
    count_extracted_units,
    distribute_topics_evenly,
    enforce_standard_model,
    flatten_extracted_topics,
    validate_topic_distribution,
)


class TopicDistributionTests(unittest.TestCase):
    def test_flatten_extracted_topics_preserves_order(self):
        units_data = {
            "Unit 1": ["A", "B"],
            "Unit 2": ["C"],
        }

        topics, warnings = flatten_extracted_topics(units_data)

        self.assertEqual(topics, ["A", "B", "C"])
        self.assertEqual(warnings, [])

    def test_distribute_topics_evenly_without_loss(self):
        topics = ["t1", "t2", "t3", "t4", "t5", "t6", "t7"]
        distributed = distribute_topics_evenly(topics, 4)

        self.assertEqual(len(distributed), 4)
        self.assertEqual([len(bucket) for bucket in distributed], [2, 2, 2, 1])
        self.assertEqual([topic for bucket in distributed for topic in bucket], topics)

    def test_enforce_standard_model_redistributes_pdf_units(self):
        structure = {
            "totalUnits": 4,
            "units": [
                {"unitNumber": 1, "topicCount": 5},
                {"unitNumber": 2, "topicCount": 5},
                {"unitNumber": 3, "topicCount": 5},
                {"unitNumber": 4, "topicCount": 5},
            ],
        }
        units_data = {
            "Unit 1": ["A", "B"],
            "Unit 2": ["C", "D", "E"],
            "Unit 3": ["F"],
            "Unit 4": ["G", "H"],
            "Unit 5": ["I"],
            "Unit 6": ["J"],
        }

        result = enforce_standard_model(structure, units_data)

        self.assertEqual(result["totalUnits"], 4)
        self.assertEqual(len(result["units"]), 4)
        self.assertEqual(
            [topic for unit in result["units"] for topic in unit["topics"]],
            ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
        )
        self.assertTrue(result["enforcement"]["topicsPreserved"])
        self.assertTrue(any("6 unit(s)" in warning for warning in result["warnings"]))

    def test_validate_topic_distribution_detects_loss(self):
        warnings = validate_topic_distribution(
            ["A", "B", "C"],
            [["A"], ["B"]],
            2,
        )

        self.assertTrue(any("Topic loss detected" in warning for warning in warnings))


if __name__ == "__main__":
    unittest.main()
