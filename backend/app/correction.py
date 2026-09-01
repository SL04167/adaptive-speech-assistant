"""Personalized correction retrieval and conservative replacement."""

from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass(frozen=True)
class CorrectionExample:
    heard: str
    intended: str
    context: str = ""


@dataclass(frozen=True)
class AppliedChange:
    source: str
    replacement: str
    confidence: float


@dataclass(frozen=True)
class CorrectionResult:
    raw_transcript: str
    corrected_transcript: str
    changes: tuple[AppliedChange, ...]


DEFAULT_EXAMPLES = [
    CorrectionExample("park in sons", "Parkinson's", "health appointment"),
    CorrectionExample("doctor patel", "Dr. Patel", "contact name"),
    CorrectionExample("carbid open", "carbidopa", "medication name"),
    CorrectionExample("physical there a pee", "physical therapy", "appointment"),
]


class CorrectionEngine:
    """Apply exact and high-confidence personalized phrase corrections."""

    def __init__(
        self,
        examples: list[CorrectionExample] | None = None,
        similarity_threshold: float = 0.72,
    ) -> None:
        self.examples = list(examples or DEFAULT_EXAMPLES)
        self.similarity_threshold = similarity_threshold
        self._vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
        corpus = [item.heard for item in self.examples]
        self._example_vectors = self._vectorizer.fit_transform(corpus)

    @staticmethod
    def _candidate_phrases(transcript: str, word_count: int) -> list[str]:
        words = re.findall(r"[A-Za-z']+", transcript.lower())
        return [
            " ".join(words[index : index + word_count])
            for index in range(len(words) - word_count + 1)
        ]

    def retrieve(self, transcript: str, limit: int = 8) -> list[tuple[str, CorrectionExample, float]]:
        results: list[tuple[str, CorrectionExample, float]] = []
        for example_index, example in enumerate(self.examples):
            word_count = len(re.findall(r"[A-Za-z']+", example.heard))
            candidates = self._candidate_phrases(transcript, word_count)
            if not candidates:
                continue
            candidate_vectors = self._vectorizer.transform(candidates)
            similarities = cosine_similarity(
                candidate_vectors, self._example_vectors[example_index]
            ).ravel()
            candidate_index = int(np.argmax(similarities))
            score = float(similarities[candidate_index])
            if score >= self.similarity_threshold:
                results.append((candidates[candidate_index], example, score))
        return sorted(results, key=lambda item: item[2], reverse=True)[:limit]

    @staticmethod
    def _replace_case_insensitive(text: str, source: str, replacement: str) -> tuple[str, bool]:
        pattern = re.compile(rf"\b{re.escape(source)}\b", flags=re.IGNORECASE)
        updated, count = pattern.subn(replacement, text, count=1)
        return updated, count > 0

    @staticmethod
    def _cleanup(text: str) -> str:
        compact = re.sub(r"\s+", " ", text).strip()
        compact = re.sub(r"\s+([,.;!?])", r"\1", compact)
        if not compact:
            return compact
        compact = compact[0].upper() + compact[1:]
        if compact[-1] not in ".!?":
            compact += "."
        return compact

    def correct(self, transcript: str) -> CorrectionResult:
        if not transcript.strip():
            raise ValueError("transcript cannot be empty")
        corrected = transcript
        changes: list[AppliedChange] = []
        retrieved = self.retrieve(transcript)
        # Longer phrases first prevents a short phrase from consuming a match.
        for candidate, example, score in sorted(retrieved, key=lambda item: len(item[0]), reverse=True):
            corrected, applied = self._replace_case_insensitive(corrected, candidate, example.intended)
            if applied:
                changes.append(
                    AppliedChange(
                        source=candidate,
                        replacement=example.intended,
                        confidence=round(score, 3),
                    )
                )
        return CorrectionResult(
            raw_transcript=transcript,
            corrected_transcript=self._cleanup(corrected),
            changes=tuple(changes),
        )
