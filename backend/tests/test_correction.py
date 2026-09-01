from __future__ import annotations

import unittest

from app.correction import CorrectionEngine, CorrectionExample


class CorrectionEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = CorrectionEngine()

    def test_exact_personal_phrase_is_corrected(self) -> None:
        result = self.engine.correct("my park in sons appointment is Friday")
        self.assertIn("Parkinson's appointment", result.corrected_transcript)
        self.assertEqual(result.changes[0].replacement, "Parkinson's")

    def test_contact_name_is_normalized(self) -> None:
        result = self.engine.correct("please call doctor patel")
        self.assertEqual(result.corrected_transcript, "Please call Dr. Patel.")

    def test_unknown_words_are_preserved(self) -> None:
        source = "meet Sam at the library at three"
        result = self.engine.correct(source)
        self.assertEqual(result.corrected_transcript, "Meet Sam at the library at three.")
        self.assertEqual(result.changes, ())

    def test_empty_input_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.engine.correct("   ")

    def test_threshold_can_disable_uncertain_matches(self) -> None:
        strict = CorrectionEngine(
            examples=[CorrectionExample("doctor patel", "Dr. Patel")],
            similarity_threshold=0.99,
        )
        result = strict.correct("please contact doctor paddle")
        self.assertEqual(result.changes, ())


if __name__ == "__main__":
    unittest.main()
