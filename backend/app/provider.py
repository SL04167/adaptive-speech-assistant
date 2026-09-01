"""Provider-neutral boundary for speech-to-text services."""

from __future__ import annotations

from typing import Protocol


class SpeechToTextProvider(Protocol):
    def transcribe(self, audio: bytes, content_type: str) -> str:
        """Return a raw transcript for the supplied audio."""


class DemoProvider:
    """Deterministic adapter used only for local demonstrations."""

    def transcribe(self, audio: bytes, content_type: str) -> str:
        del audio, content_type
        return "please email doctor patel about the park in sons appointment"
