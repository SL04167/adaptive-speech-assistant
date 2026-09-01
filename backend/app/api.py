"""FastAPI interface for text correction and demo transcription."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .correction import CorrectionEngine


app = FastAPI(title="Adaptive Speech Assistant", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
engine = CorrectionEngine()


class AssistRequest(BaseModel):
    raw_transcript: str = Field(min_length=1, max_length=5000)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/assist")
def assist(request: AssistRequest) -> dict[str, object]:
    return asdict(engine.correct(request.raw_transcript))
