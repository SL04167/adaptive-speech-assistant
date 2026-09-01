import { useState } from "react";

type Change = { source: string; replacement: string; confidence: number };
type Result = { corrected_transcript: string; changes: Change[] };

const sample = "please email doctor patel about the park in sons appointment";

export default function App() {
  const [raw, setRaw] = useState(sample);
  const [result, setResult] = useState<Result | null>(null);
  const [copied, setCopied] = useState(false);

  async function improve() {
    const response = await fetch("http://localhost:8000/assist", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ raw_transcript: raw }),
    });
    setResult(await response.json());
    setCopied(false);
  }

  async function copy() {
    if (!result) return;
    await navigator.clipboard.writeText(result.corrected_transcript);
    setCopied(true);
  }

  return (
    <main>
      <nav>
        <a className="brand" href="#main">Clear<span>Voice</span></a>
        <div><span className="privacy-dot" /> Private demo</div>
      </nav>

      <section className="hero" id="main">
        <p className="kicker">PERSONALIZED TRANSCRIPTION</p>
        <h1>Your words,<br /><em>more clearly.</em></h1>
        <p className="intro">A correction layer that learns recurring speech-to-text errors while keeping every edit visible and reversible.</p>
      </section>

      <section className="workspace" aria-label="Transcript editor">
        <div className="panel">
          <label htmlFor="raw">Raw transcript</label>
          <textarea id="raw" value={raw} onChange={(event) => setRaw(event.target.value)} />
          <button className="primary" onClick={improve}>Improve transcript <span>→</span></button>
        </div>

        <div className="panel result-panel">
          <div className="result-heading">
            <label htmlFor="result">Corrected text</label>
            {result && <span>{result.changes.length} personal corrections</span>}
          </div>
          <textarea
            id="result"
            value={result?.corrected_transcript ?? "Your corrected transcript will appear here."}
            onChange={(event) => setResult((current) => current ? { ...current, corrected_transcript: event.target.value } : null)}
            className={!result ? "placeholder" : ""}
          />
          <button className="secondary" onClick={copy} disabled={!result}>{copied ? "Copied" : "Copy text"}</button>
        </div>
      </section>

      {result && result.changes.length > 0 && (
        <section className="changes">
          <p className="kicker">WHAT CHANGED</p>
          {result.changes.map((change) => (
            <div className="change" key={`${change.source}-${change.replacement}`}>
              <span className="before">{change.source}</span><span>→</span>
              <strong>{change.replacement}</strong>
              <small>{Math.round(change.confidence * 100)}% match</small>
            </div>
          ))}
        </section>
      )}
    </main>
  );
}
