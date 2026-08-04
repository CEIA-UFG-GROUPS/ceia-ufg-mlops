import json
import unittest

from src.common import make_credit_dataset
from src.explain import explain_lime, explain_shap
from src.fairness import assess
from src.rag_retrieve import retrieve
from src.train_model import train


class Aula24Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.metrics = train(seed=42)

    def test_dataset_is_deterministic(self) -> None:
        first = make_credit_dataset(seed=42)
        second = make_credit_dataset(seed=42)
        self.assertTrue(first.equals(second))

    def test_protected_attribute_is_not_a_feature(self) -> None:
        from src.common import bundle_path

        bundle = __import__("joblib").load(bundle_path())
        self.assertNotIn("protected_group", bundle["feature_columns"])

    def test_training_is_reproducible(self) -> None:
        self.assertEqual(self.metrics, train(seed=42))

    def test_shap_outputs_global_and_local_artifacts(self) -> None:
        result = explain_shap(row_index=0)
        for path in result.values():
            self.assertTrue(__import__("pathlib").Path(path).exists())

    def test_lime_outputs_html_and_json(self) -> None:
        result = explain_lime(row_index=0)
        self.assertTrue(__import__("pathlib").Path(result["html"]).exists())
        payload = json.loads(__import__("pathlib").Path(result["json"]).read_text(encoding="utf-8"))
        self.assertTrue(payload["contributions"])

    def test_fairness_contains_group_metrics(self) -> None:
        result = assess()
        self.assertIn("demographic_parity_difference", result)
        self.assertIn("equalized_odds_difference", result)
        self.assertFalse(result["protected_group_column_used_as_feature"])

    def test_rag_retrieval_returns_sources(self) -> None:
        result = retrieve("quando usar RAG em vez de fine-tuning?", top_k=3)
        self.assertTrue(result["hits"])
        self.assertIn("source", result["hits"][0])
        self.assertIn("Contexto:", result["prompt"])


if __name__ == "__main__":
    unittest.main()
