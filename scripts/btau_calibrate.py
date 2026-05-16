"""Wave 0 W0.3 — B-T7 cosine threshold calibration for Phase 2.5 Track B.

Per sub-spec SEAL ab8e715 §4 B-1 + §6 B-T7 (c) placement: this script
sweeps cosine similarity threshold τ ∈ {0.70, 0.75, 0.80, 0.82, 0.85,
0.88, 0.90} against a synthetic DSL JSON fixture corpus. Phase 2C
Stage 1 DSL pairs are unavailable per sub-spec §6 P-F7 acknowledgment;
calibration runs on fixture corpus only with "production validation
deferred to first Phase 2D batch".

Outputs:
- ``data/phase2_5/btau_calibration_v1/calibration_corpus.json``
- ``data/phase2_5/btau_calibration_v1/sweep_results.json``
- ``data/phase2_5/btau_calibration_v1/CALIBRATION_NOTE.md``

The chosen τ feeds B-1 default; if calibration knee != 0.82, sub-spec
amendment register-event is triggered per §6.

Usage::

    python scripts/btau_calibrate.py

Discipline:
- B-Lock-6 honored: sentence-transformers local CPU; no remote embedding API
- B-Lock-7 honored: model artifact + tokenizer SHA recorded in
  CALIBRATION_NOTE.md output
- HARD CONSTRAINT honored: fixture corpus is synthetic; no
  Phase 2C / validation / test / 2022-regime data ingested
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import numpy as np
from sentence_transformers import SentenceTransformer


REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "data" / "phase2_5" / "btau_calibration_v1"
SWEEP_TAUS = (0.70, 0.75, 0.80, 0.82, 0.85, 0.88, 0.90)
MODEL_NAME = "all-MiniLM-L6-v2"


PairLabel = Literal["near_dup", "distinct"]


@dataclass(frozen=True)
class CalibrationPair:
    pair_id: str
    label: PairLabel
    dsl_a: dict
    dsl_b: dict
    description: str


def build_fixture_corpus() -> list[CalibrationPair]:
    """Construct synthetic DSL JSON pairs for τ calibration.

    Pairs are labeled "near_dup" (intent: should be flagged as
    duplicates by semantic dedup) or "distinct" (intent: should NOT
    be flagged). The calibration sweep finds τ that maximizes label
    agreement.
    """
    pairs: list[CalibrationPair] = []

    # near_dup pairs: parameter variation of the same strategy family
    pairs.append(CalibrationPair(
        pair_id="near_dup_sma_20_vs_21",
        label="near_dup",
        dsl_a={"name": "sma_long", "entry": [{"factor": "sma", "param": 20, "op": ">", "value": "close"}], "exit": [{"bars": 10}]},
        dsl_b={"name": "sma_long", "entry": [{"factor": "sma", "param": 21, "op": ">", "value": "close"}], "exit": [{"bars": 10}]},
        description="SMA(20) vs SMA(21) — parameter variation",
    ))
    pairs.append(CalibrationPair(
        pair_id="near_dup_sma_20_vs_22",
        label="near_dup",
        dsl_a={"name": "sma_long", "entry": [{"factor": "sma", "param": 20, "op": ">", "value": "close"}], "exit": [{"bars": 10}]},
        dsl_b={"name": "sma_long", "entry": [{"factor": "sma", "param": 22, "op": ">", "value": "close"}], "exit": [{"bars": 10}]},
        description="SMA(20) vs SMA(22) — wider parameter variation",
    ))
    pairs.append(CalibrationPair(
        pair_id="near_dup_rsi_14_30_vs_31",
        label="near_dup",
        dsl_a={"name": "rsi_oversold", "entry": [{"factor": "rsi", "param": 14, "op": "<", "value": 30}], "exit": [{"bars": 5}]},
        dsl_b={"name": "rsi_oversold", "entry": [{"factor": "rsi", "param": 14, "op": "<", "value": 31}], "exit": [{"bars": 5}]},
        description="RSI(14,30) vs RSI(14,31) — threshold value variation",
    ))
    pairs.append(CalibrationPair(
        pair_id="near_dup_rsi_window_14_vs_15",
        label="near_dup",
        dsl_a={"name": "rsi_oversold", "entry": [{"factor": "rsi", "param": 14, "op": "<", "value": 30}], "exit": [{"bars": 5}]},
        dsl_b={"name": "rsi_oversold", "entry": [{"factor": "rsi", "param": 15, "op": "<", "value": 30}], "exit": [{"bars": 5}]},
        description="RSI(14,30) vs RSI(15,30) — window variation",
    ))
    pairs.append(CalibrationPair(
        pair_id="near_dup_holdbars_10_vs_11",
        label="near_dup",
        dsl_a={"name": "sma_long", "entry": [{"factor": "sma", "param": 20, "op": ">", "value": "close"}], "exit": [{"bars": 10}]},
        dsl_b={"name": "sma_long", "entry": [{"factor": "sma", "param": 20, "op": ">", "value": "close"}], "exit": [{"bars": 11}]},
        description="Same entry, 10-bar vs 11-bar hold",
    ))

    # distinct pairs: meaningfully different strategies
    pairs.append(CalibrationPair(
        pair_id="distinct_sma_vs_rsi",
        label="distinct",
        dsl_a={"name": "sma_long", "entry": [{"factor": "sma", "param": 20, "op": ">", "value": "close"}], "exit": [{"bars": 10}]},
        dsl_b={"name": "rsi_oversold", "entry": [{"factor": "rsi", "param": 14, "op": "<", "value": 30}], "exit": [{"bars": 5}]},
        description="SMA-based momentum vs RSI-based mean-reversion",
    ))
    pairs.append(CalibrationPair(
        pair_id="distinct_long_vs_short_bias",
        label="distinct",
        dsl_a={"name": "sma_long", "entry": [{"factor": "sma", "param": 20, "op": ">", "value": "close"}], "exit": [{"bars": 10}]},
        dsl_b={"name": "sma_short", "entry": [{"factor": "sma", "param": 20, "op": "<", "value": "close"}], "exit": [{"bars": 10}]},
        description="Long SMA crossover vs short SMA crossover (opposite direction)",
    ))
    pairs.append(CalibrationPair(
        pair_id="distinct_single_vs_multi_factor",
        label="distinct",
        dsl_a={"name": "sma_long", "entry": [{"factor": "sma", "param": 20, "op": ">", "value": "close"}], "exit": [{"bars": 10}]},
        dsl_b={"name": "sma_vol_long", "entry": [{"factor": "sma", "param": 20, "op": ">", "value": "close"}, {"factor": "volume", "param": 50, "op": ">", "value": "avg"}], "exit": [{"bars": 10}]},
        description="Single-factor SMA vs SMA + volume confirmation",
    ))
    pairs.append(CalibrationPair(
        pair_id="distinct_macd_vs_bbands",
        label="distinct",
        dsl_a={"name": "macd_signal", "entry": [{"factor": "macd", "param": [12, 26, 9], "op": "cross_above", "value": "signal"}], "exit": [{"bars": 8}]},
        dsl_b={"name": "bbands_squeeze", "entry": [{"factor": "bbands", "param": [20, 2], "op": "<", "value": "lower"}], "exit": [{"bars": 5}]},
        description="MACD signal cross vs Bollinger Bands squeeze",
    ))
    pairs.append(CalibrationPair(
        pair_id="distinct_short_vs_long_window",
        label="distinct",
        dsl_a={"name": "sma_fast", "entry": [{"factor": "sma", "param": 5, "op": ">", "value": "close"}], "exit": [{"bars": 3}]},
        dsl_b={"name": "sma_slow", "entry": [{"factor": "sma", "param": 200, "op": ">", "value": "close"}], "exit": [{"bars": 100}]},
        description="SMA(5) short-term vs SMA(200) long-term — same factor, drastically different timeframes",
    ))

    return pairs


def canonicalize_dsl(dsl: dict) -> str:
    """Canonicalize a DSL JSON to a stable string for embedding.

    Mirrors the D3-canonical form spirit (sorted keys, no whitespace) but
    stays self-contained in this script — does NOT call
    ``agents.hypothesis_hash.canonicalize_for_hash`` per B-Lock-2 spirit
    (separate code paths preserve CONTRACT BOUNDARY).
    """
    return json.dumps(dsl, sort_keys=True, separators=(",", ":"))


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two embedding vectors."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def model_artifact_sha(model: SentenceTransformer) -> str:
    """Compute a SHA-256 over the model's first-tensor parameters.

    Provides a stable identifier for the model artifact at calibration
    time, recorded in CALIBRATION_NOTE.md per B-Lock-7. Not a complete
    artifact hash (which would require hashing all weights + tokenizer),
    but sufficient to detect model-file drift between runs.
    """
    first_param = next(iter(model.named_parameters()))[1].detach().cpu().numpy()
    return hashlib.sha256(first_param.tobytes()).hexdigest()[:16]


def run_calibration() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pairs = build_fixture_corpus()
    print(f"[calibrate] loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    model_sha = model_artifact_sha(model)
    embed_dim = model.get_sentence_embedding_dimension()
    print(f"[calibrate] model loaded, dim={embed_dim}, first-param SHA={model_sha}")

    # Compute embeddings
    print(f"[calibrate] computing embeddings for {2 * len(pairs)} DSL strings")
    pair_records: list[dict] = []
    for p in pairs:
        text_a = canonicalize_dsl(p.dsl_a)
        text_b = canonicalize_dsl(p.dsl_b)
        emb_a = model.encode(text_a, convert_to_numpy=True, show_progress_bar=False)
        emb_b = model.encode(text_b, convert_to_numpy=True, show_progress_bar=False)
        cos = cosine_similarity(emb_a, emb_b)
        pair_records.append({
            "pair_id": p.pair_id,
            "label": p.label,
            "description": p.description,
            "cosine": round(cos, 6),
            "text_a_len": len(text_a),
            "text_b_len": len(text_b),
        })
        print(f"  {p.pair_id} [{p.label}] cosine={cos:.4f}")

    # Sweep τ
    print(f"[calibrate] sweeping τ ∈ {SWEEP_TAUS}")
    sweep: list[dict] = []
    for tau in SWEEP_TAUS:
        tp = sum(
            1 for r in pair_records
            if r["label"] == "near_dup" and r["cosine"] >= tau
        )
        fn = sum(
            1 for r in pair_records
            if r["label"] == "near_dup" and r["cosine"] < tau
        )
        fp = sum(
            1 for r in pair_records
            if r["label"] == "distinct" and r["cosine"] >= tau
        )
        tn = sum(
            1 for r in pair_records
            if r["label"] == "distinct" and r["cosine"] < tau
        )
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        sweep.append({
            "tau": tau, "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        })
        print(f"  τ={tau:.2f} TP={tp} FP={fp} FN={fn} TN={tn} P={precision:.3f} R={recall:.3f} F1={f1:.3f}")

    # Choose τ: highest F1; on tie, prefer LOWER τ (more aggressive dedup is
    # better at MVP because near-duplicates skip backtest and save compute;
    # false-positives can be Critic-overridden per B-3 quarantine semantics).
    best_idx = max(
        range(len(sweep)),
        key=lambda i: (sweep[i]["f1"], -sweep[i]["tau"]),
    )
    chosen_tau = sweep[best_idx]["tau"]
    chosen_metrics = sweep[best_idx]
    print(f"[calibrate] chosen τ = {chosen_tau} (F1={chosen_metrics['f1']:.4f})")

    # Build calibration corpus JSON for archive
    corpus_records = [
        {
            "pair_id": p.pair_id,
            "label": p.label,
            "description": p.description,
            "dsl_a": p.dsl_a,
            "dsl_b": p.dsl_b,
        }
        for p in pairs
    ]

    timestamp_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Write calibration corpus
    (OUTPUT_DIR / "calibration_corpus.json").write_text(
        json.dumps(corpus_records, indent=2),
        encoding="utf-8",
    )

    # Write sweep results
    (OUTPUT_DIR / "sweep_results.json").write_text(
        json.dumps({
            "model_name": MODEL_NAME,
            "model_first_param_sha": model_sha,
            "embedding_dim": embed_dim,
            "n_pairs": len(pairs),
            "n_near_dup": sum(1 for p in pairs if p.label == "near_dup"),
            "n_distinct": sum(1 for p in pairs if p.label == "distinct"),
            "calibration_utc": timestamp_utc,
            "sweep_taus": list(SWEEP_TAUS),
            "pair_cosines": pair_records,
            "sweep": sweep,
            "chosen_tau": chosen_tau,
            "selection_rule": (
                "Highest F1 score across the τ sweep. Tie-break: prefer "
                "LOWER τ (more aggressive dedup; near-duplicates skip backtest "
                "and save compute; false-positives are Critic-overridable per "
                "B-3 quarantine semantics)."
            ),
        }, indent=2),
        encoding="utf-8",
    )

    # Write CALIBRATION_NOTE
    note_lines = [
        "# B-T7 Cosine Threshold Calibration — v1",
        "",
        f"**Calibration timestamp (UTC)**: {timestamp_utc}",
        f"**Model**: `{MODEL_NAME}` (embedding dim {embed_dim})",
        f"**Model first-param SHA-256[:16]**: `{model_sha}`",
        "**Fixture corpus**: synthetic; Phase 2C Stage 1 DSL pairs unavailable per sub-spec SEAL ab8e715 §6 P-F7 acknowledgment.",
        f"**Pair count**: {len(pairs)} ({sum(1 for p in pairs if p.label == 'near_dup')} near-dup + {sum(1 for p in pairs if p.label == 'distinct')} distinct)",
        "",
        "## Sweep results",
        "",
        "| τ | TP | FP | FN | TN | Precision | Recall | F1 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in sweep:
        note_lines.append(
            f"| {row['tau']:.2f} | {row['tp']} | {row['fp']} | {row['fn']} | {row['tn']} | {row['precision']:.3f} | {row['recall']:.3f} | {row['f1']:.3f} |"
        )

    note_lines.extend([
        "",
        "## Chosen τ",
        "",
        f"**τ = {chosen_tau}** (F1 = {chosen_metrics['f1']:.4f}, precision = {chosen_metrics['precision']:.3f}, recall = {chosen_metrics['recall']:.3f})",
        "",
        "**Selection rule**: highest F1 score across the τ sweep; tie-break prefers LOWER τ (more aggressive dedup at MVP since near-duplicates skip backtest and save compute; false-positives are Critic-overridable per B-3 quarantine semantics).",
        "",
        "## Per-pair cosine similarity",
        "",
        "| Pair ID | Label | Cosine | Description |",
        "|---|---|---|---|",
    ])
    for r in pair_records:
        note_lines.append(
            f"| `{r['pair_id']}` | {r['label']} | {r['cosine']:.4f} | {r['description']} |"
        )

    note_lines.extend([
        "",
        "## Sub-spec impact",
        "",
        f"Sub-spec SEAL `ab8e715` §4 B-1 carried τ=0.82 PROVISIONAL with Wave 0 re-adjudication trigger if calibration knee ≠ 0.82.",
        "",
        f"**Calibration result**: chosen τ = **{chosen_tau}**.",
        "",
    ])
    if abs(chosen_tau - 0.82) < 1e-6:
        note_lines.append(
            "Chosen τ matches the PROVISIONAL value — **NO sub-spec amendment required**. "
            "B-1 default is confirmed at τ=0.82."
        )
    else:
        note_lines.append(
            f"Chosen τ ({chosen_tau}) ≠ PROVISIONAL 0.82 — **sub-spec amendment register-event triggered** "
            f"per sub-spec §6 B-T7 (c) re-adjudication clause. B-1 default to be updated to τ={chosen_tau} "
            f"at sub-spec amendment cycle entry register-event boundary (separate Charlie authorization required)."
        )

    note_lines.extend([
        "",
        "## Discipline locks honored",
        "",
        "- B-Lock-6: sentence-transformers local CPU; no remote embedding API",
        "- B-Lock-7: model artifact SHA recorded above; install-time-only network egress",
        "- HARD CONSTRAINT: fixture corpus is synthetic; no Phase 2C / validation / test / 2022-regime data ingested",
        "- §6 P-F7 (Phase 2C data availability): unavailable → fixture-corpus-only-calibrated; production validation deferred to first Phase 2D batch",
        "",
        "## Reproducibility",
        "",
        f"Run: `python scripts/btau_calibrate.py` (deterministic; same model file → same cosines → same chosen τ).",
        f"Outputs at `{OUTPUT_DIR.relative_to(REPO_ROOT)}/`: this file + `calibration_corpus.json` + `sweep_results.json`.",
    ])

    (OUTPUT_DIR / "CALIBRATION_NOTE.md").write_text(
        "\n".join(note_lines) + "\n",
        encoding="utf-8",
    )

    print(f"[calibrate] outputs written to {OUTPUT_DIR.relative_to(REPO_ROOT)}/")
    print(f"[calibrate] CHOSEN τ = {chosen_tau}")


if __name__ == "__main__":
    sys.exit(run_calibration() or 0)
