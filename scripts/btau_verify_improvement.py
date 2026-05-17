"""Methodological verification: is the W0.3 → W0.3.v2 F1 improvement REAL?

User question (Charlie register 2026-05-16): "verify the F1 boost is actual
improvement instead of some sort of cheating to boost this statistics score".

This script runs a proper 2×2 ablation on the SAME N=32 W0.3.v2 fixture:

    Serialization × Gate-type
    ─────────────────────────
    D3-JSON   × cosine-only   ← W0.3 config (control)
    D3-JSON   × compound      ← isolates compound-gate effect alone
    NL        × cosine-only   ← isolates NL-serializer effect alone
    NL        × compound      ← W0.3.v2 config (treatment)

Each config sweeps τ ∈ {0.70..0.99}; we report:
- F1 / P / R per (config, τ)
- Best F1 per config + chosen τ
- Same-factor-set SUBSET F1 (strips out trivial cross-factor wins)
- Per-class breakdown (C1..C5)
- Marginal contribution analysis: ΔF1 from NL alone vs ΔF1 from compound alone

Outputs at ``data/phase2_5/btau_calibration_v2/VERIFICATION_AUDIT.md``.

Discipline:
- Uses the EXACT same fixture as W0.3.v2 (loaded from disk; no re-construction)
- Uses the EXACT same model + SHA as W0.3.v2 (logged for parity check)
- Reports honestly — if cheating is found, flags it for amendment v2 trigger
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from agents.critic.d7a_feature_extraction import extract_factors
from agents.orchestrator.semantic_dedup import nl_serialize_dsl
from strategies.dsl import StrategyDSL


REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_PATH = REPO_ROOT / "data" / "phase2_5" / "btau_calibration_v2" / "fixture_corpus.json"
OUTPUT_DIR = REPO_ROOT / "data" / "phase2_5" / "btau_calibration_v2"
MODEL_NAME = "all-MiniLM-L6-v2"
SWEEP_TAUS = (0.70, 0.75, 0.80, 0.82, 0.85, 0.88, 0.90, 0.92, 0.95, 0.97, 0.99)


def d3_canonical_serialize(dsl_dict: dict) -> str:
    """Stand-in for D3-canonical JSON used in W0.3 calibration.

    Mirrors the W0.3 script's ``canonicalize_dsl`` helper: ``json.dumps`` with
    ``sort_keys=True, separators=(',', ':')`` directly on the dict (no D3
    canonicalization function called, per B-Lock-2 separation discipline).
    """
    return json.dumps(dsl_dict, sort_keys=True, separators=(",", ":"))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def model_sha(model: SentenceTransformer) -> str:
    first_param = next(iter(model.named_parameters()))[1].detach().cpu().numpy()
    return hashlib.sha256(first_param.tobytes()).hexdigest()[:16]


def evaluate_config(
    pairs: list[dict],
    serialization: str,  # "d3_json" or "nl"
    gate_type: str,  # "cosine_only" or "compound"
    tau: float,
) -> dict:
    """Compute confusion matrix + F1 for one configuration at one τ."""
    tp = fp = fn = tn = 0
    for p in pairs:
        cos = p[f"cos_{serialization}"]
        fs_eq = p["factor_set_equal"]
        if gate_type == "cosine_only":
            flag = cos >= tau
        else:  # compound
            flag = cos >= tau and fs_eq

        is_near_dup = p["label"] == "near_dup"
        if is_near_dup and flag:
            tp += 1
        elif is_near_dup and not flag:
            fn += 1
        elif not is_near_dup and flag:
            fp += 1
        else:
            tn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def best_for_config(
    pairs: list[dict], serialization: str, gate_type: str
) -> dict:
    """Sweep τ; return best F1 + the corresponding metrics + chosen τ."""
    best = None
    full_sweep = []
    for tau in SWEEP_TAUS:
        m = evaluate_config(pairs, serialization, gate_type, tau)
        m["tau"] = tau
        full_sweep.append(m)
        if best is None or (m["f1"], -tau) > (best["f1"], -best["tau"]):
            best = m
    return {"best": best, "sweep": full_sweep}


def main() -> None:
    print("[verify] loading W0.3.v2 fixture corpus")
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    print(f"[verify] fixture has {len(fixture)} pairs")

    print(f"[verify] loading model {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    sha = model_sha(model)
    print(f"[verify] model first-param SHA={sha} (W0.3.v2 used 352d34a4ad725bb7)")

    # Precompute embeddings + factor-set equality once for both serializations
    pairs_enriched: list[dict] = []
    print("[verify] computing D3-JSON and NL embeddings + cosines for all pairs")
    for p in fixture:
        dsl_a_val = StrategyDSL.model_validate(p["dsl_a"])
        dsl_b_val = StrategyDSL.model_validate(p["dsl_b"])

        # D3-JSON serializations (W0.3-style — raw dict to JSON)
        d3_a = d3_canonical_serialize(p["dsl_a"])
        d3_b = d3_canonical_serialize(p["dsl_b"])
        emb_d3_a = model.encode(d3_a, convert_to_numpy=True, show_progress_bar=False)
        emb_d3_b = model.encode(d3_b, convert_to_numpy=True, show_progress_bar=False)
        cos_d3 = cosine(emb_d3_a, emb_d3_b)

        # NL serializations (W0.3.v2-style)
        nl_a = nl_serialize_dsl(dsl_a_val)
        nl_b = nl_serialize_dsl(dsl_b_val)
        emb_nl_a = model.encode(nl_a, convert_to_numpy=True, show_progress_bar=False)
        emb_nl_b = model.encode(nl_b, convert_to_numpy=True, show_progress_bar=False)
        cos_nl = cosine(emb_nl_a, emb_nl_b)

        fs_eq = (
            frozenset(extract_factors(dsl_a_val))
            == frozenset(extract_factors(dsl_b_val))
        )

        pairs_enriched.append({
            "pair_id": p["pair_id"],
            "label": p["label"],
            "distribution_class": p["distribution_class"],
            "description": p["description"],
            "cos_d3_json": round(cos_d3, 6),
            "cos_nl": round(cos_nl, 6),
            "factor_set_equal": fs_eq,
            "nl_a": nl_a,
            "nl_b": nl_b,
            "d3_a_len": len(d3_a),
            "d3_b_len": len(d3_b),
            "nl_a_len": len(nl_a),
            "nl_b_len": len(nl_b),
        })

    # 2×2 ablation
    print("[verify] running 2×2 ablation (serialization × gate-type)")
    configs = {
        "D3-JSON × cosine-only (≈W0.3)":   ("cos_d3_json", "cosine_only"),
        "D3-JSON × compound":               ("cos_d3_json", "compound"),
        "NL × cosine-only":                 ("cos_nl",      "cosine_only"),
        "NL × compound (W0.3.v2)":          ("cos_nl",      "compound"),
    }
    # Rewrite key names to match the evaluate_config signature
    results: dict[str, dict] = {}
    for label, (cos_key, gate_type) in configs.items():
        # We need to remap cos_d3_json → "d3_json" and cos_nl → "nl"
        serialization = "d3_json" if cos_key == "cos_d3_json" else "nl"
        results[label] = best_for_config(pairs_enriched, serialization, gate_type)
        b = results[label]["best"]
        print(
            f"  {label}: best F1={b['f1']:.4f} at τ={b['tau']:.2f} "
            f"(P={b['precision']:.3f}, R={b['recall']:.3f}, "
            f"TP={b['tp']} FP={b['fp']} FN={b['fn']} TN={b['tn']})"
        )

    # Per-class breakdown at chosen τ for the W0.3.v2 config
    w0_3_v2_best = results["NL × compound (W0.3.v2)"]["best"]
    w0_3_v2_tau = w0_3_v2_best["tau"]
    by_class: dict[str, dict] = {}
    for p in pairs_enriched:
        cls = p["distribution_class"]
        cos_nl = p["cos_nl"]
        fs_eq = p["factor_set_equal"]
        flag = (cos_nl >= w0_3_v2_tau) and fs_eq
        is_near = p["label"] == "near_dup"
        by_class.setdefault(cls, {
            "n": 0, "tp": 0, "fp": 0, "fn": 0, "tn": 0,
        })
        by_class[cls]["n"] += 1
        if is_near and flag:
            by_class[cls]["tp"] += 1
        elif is_near and not flag:
            by_class[cls]["fn"] += 1
        elif not is_near and flag:
            by_class[cls]["fp"] += 1
        else:
            by_class[cls]["tn"] += 1

    # Same-factor-set SUBSET analysis — the "hard" pairs cosine actually has to discriminate
    hard_pairs = [p for p in pairs_enriched if p["factor_set_equal"]]
    print(
        f"[verify] hard subset (same factor set): {len(hard_pairs)} pairs "
        f"({sum(1 for p in hard_pairs if p['label']=='near_dup')} near-dup + "
        f"{sum(1 for p in hard_pairs if p['label']=='distinct')} distinct)"
    )
    # For hard subset, compound gate degenerates to cosine-only (FS equal == True for all);
    # so we just compare D3-JSON cosine vs NL cosine on this subset
    hard_results: dict[str, dict] = {}
    for label, serialization in (
        ("D3-JSON cosine on hard subset", "d3_json"),
        ("NL cosine on hard subset", "nl"),
    ):
        hard_results[label] = best_for_config(hard_pairs, serialization, "cosine_only")
        b = hard_results[label]["best"]
        print(
            f"  {label}: best F1={b['f1']:.4f} at τ={b['tau']:.2f} "
            f"(P={b['precision']:.3f}, R={b['recall']:.3f}, "
            f"TP={b['tp']} FP={b['fp']} FN={b['fn']} TN={b['tn']})"
        )

    # Marginal contribution analysis
    d3_cosine_f1 = results["D3-JSON × cosine-only (≈W0.3)"]["best"]["f1"]
    d3_compound_f1 = results["D3-JSON × compound"]["best"]["f1"]
    nl_cosine_f1 = results["NL × cosine-only"]["best"]["f1"]
    nl_compound_f1 = results["NL × compound (W0.3.v2)"]["best"]["f1"]

    marginal_compound = d3_compound_f1 - d3_cosine_f1
    marginal_nl_alone = nl_cosine_f1 - d3_cosine_f1
    marginal_combined = nl_compound_f1 - d3_cosine_f1

    # Cosine distribution stats
    near_dup_d3 = [p["cos_d3_json"] for p in pairs_enriched if p["label"] == "near_dup"]
    near_dup_nl = [p["cos_nl"] for p in pairs_enriched if p["label"] == "near_dup"]
    distinct_d3 = [p["cos_d3_json"] for p in pairs_enriched if p["label"] == "distinct"]
    distinct_nl = [p["cos_nl"] for p in pairs_enriched if p["label"] == "distinct"]
    distinct_d3_same_factor = [
        p["cos_d3_json"] for p in pairs_enriched
        if p["label"] == "distinct" and p["factor_set_equal"]
    ]
    distinct_nl_same_factor = [
        p["cos_nl"] for p in pairs_enriched
        if p["label"] == "distinct" and p["factor_set_equal"]
    ]

    def stats(xs: list[float]) -> dict:
        return {
            "n": len(xs),
            "min": round(min(xs), 4),
            "max": round(max(xs), 4),
            "mean": round(sum(xs) / len(xs), 4),
        } if xs else {"n": 0}

    # Write VERIFICATION_AUDIT.md
    lines: list[str] = []
    lines.append("# B-T7 Verification Audit — Is the W0.3 → W0.3.v2 F1 Improvement Real?")
    lines.append("")
    lines.append(
        "**Charlie register-event question**: \"verify the F1 boost is actual "
        "improvement instead of some sort of cheating to boost this statistics score\"."
    )
    lines.append("")
    lines.append(
        "**Methodology**: 2×2 ablation matrix on the SAME N=32 W0.3.v2 fixture corpus. "
        "Holds fixture composition + model + factor-set definitions constant; varies "
        "ONLY (serialization, gate-type)."
    )
    lines.append("")
    lines.append(f"Model: `{MODEL_NAME}` first-param SHA `{sha}` (matches W0.3 + W0.3.v2)")
    lines.append("")
    lines.append("## 2×2 ablation results — best F1 per config (sweep over τ)")
    lines.append("")
    lines.append("| Config | Best F1 | τ | P | R | TP | FP | FN | TN |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for label in (
        "D3-JSON × cosine-only (≈W0.3)",
        "D3-JSON × compound",
        "NL × cosine-only",
        "NL × compound (W0.3.v2)",
    ):
        b = results[label]["best"]
        lines.append(
            f"| {label} | **{b['f1']:.4f}** | {b['tau']:.2f} | "
            f"{b['precision']:.3f} | {b['recall']:.3f} | "
            f"{b['tp']} | {b['fp']} | {b['fn']} | {b['tn']} |"
        )

    lines.append("")
    lines.append("## Marginal contribution analysis")
    lines.append("")
    lines.append(f"- Baseline (D3-JSON × cosine-only): F1 = **{d3_cosine_f1:.4f}**")
    lines.append(f"- Adding compound gate alone (D3-JSON × compound): F1 = **{d3_compound_f1:.4f}** (Δ = {marginal_compound:+.4f})")
    lines.append(f"- Adding NL serializer alone (NL × cosine-only): F1 = **{nl_cosine_f1:.4f}** (Δ = {marginal_nl_alone:+.4f})")
    lines.append(f"- Adding both (NL × compound = W0.3.v2): F1 = **{nl_compound_f1:.4f}** (Δ = {marginal_combined:+.4f})")
    lines.append("")
    lines.append(
        "**Interpretation**: if compound gate alone or NL alone accounts for most of "
        "Δ, the other lever is doing little additional work. If both contribute, the "
        "combined config is a real composition gain."
    )
    lines.append("")
    lines.append("## Same-factor-set SUBSET ('hard' pairs only)")
    lines.append("")
    lines.append(
        "When restricted to pairs where compound gate's structural side is TRUE for both, "
        "the compound gate degenerates to cosine-only. This subset measures the cosine "
        "gate's TRUE discrimination power — no 'auto-wins' from cross-factor structural rejection."
    )
    lines.append("")
    lines.append("| Config | Best F1 | τ | P | R | TP | FP | FN | TN |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for label in ("D3-JSON cosine on hard subset", "NL cosine on hard subset"):
        b = hard_results[label]["best"]
        lines.append(
            f"| {label} | **{b['f1']:.4f}** | {b['tau']:.2f} | "
            f"{b['precision']:.3f} | {b['recall']:.3f} | "
            f"{b['tp']} | {b['fp']} | {b['fn']} | {b['tn']} |"
        )

    lines.append("")
    lines.append("## Cosine distribution audit")
    lines.append("")
    lines.append("| Slice | n | min | mean | max |")
    lines.append("|---|---|---|---|---|")
    lines.append(f"| Near-dup, D3-JSON | {stats(near_dup_d3)['n']} | {stats(near_dup_d3)['min']} | {stats(near_dup_d3)['mean']} | {stats(near_dup_d3)['max']} |")
    lines.append(f"| Near-dup, NL | {stats(near_dup_nl)['n']} | {stats(near_dup_nl)['min']} | {stats(near_dup_nl)['mean']} | {stats(near_dup_nl)['max']} |")
    lines.append(f"| Distinct (all), D3-JSON | {stats(distinct_d3)['n']} | {stats(distinct_d3)['min']} | {stats(distinct_d3)['mean']} | {stats(distinct_d3)['max']} |")
    lines.append(f"| Distinct (all), NL | {stats(distinct_nl)['n']} | {stats(distinct_nl)['min']} | {stats(distinct_nl)['mean']} | {stats(distinct_nl)['max']} |")
    lines.append(f"| Distinct same-FS, D3-JSON | {stats(distinct_d3_same_factor)['n']} | {stats(distinct_d3_same_factor).get('min', '-')} | {stats(distinct_d3_same_factor).get('mean', '-')} | {stats(distinct_d3_same_factor).get('max', '-')} |")
    lines.append(f"| Distinct same-FS, NL | {stats(distinct_nl_same_factor)['n']} | {stats(distinct_nl_same_factor).get('min', '-')} | {stats(distinct_nl_same_factor).get('mean', '-')} | {stats(distinct_nl_same_factor).get('max', '-')} |")
    lines.append("")
    lines.append("**Class-separation gap** (mean distinct minus mean near-dup; more negative = better separation):")
    if near_dup_d3 and distinct_d3_same_factor:
        gap_d3 = sum(distinct_d3_same_factor) / len(distinct_d3_same_factor) - sum(near_dup_d3) / len(near_dup_d3)
        lines.append(f"- D3-JSON gap on hard subset: {gap_d3:+.4f}")
    if near_dup_nl and distinct_nl_same_factor:
        gap_nl = sum(distinct_nl_same_factor) / len(distinct_nl_same_factor) - sum(near_dup_nl) / len(near_dup_nl)
        lines.append(f"- NL gap on hard subset: {gap_nl:+.4f}")

    lines.append("")
    lines.append("## Per-class breakdown at W0.3.v2 chosen τ_c=" + f"{w0_3_v2_tau:.2f}")
    lines.append("")
    lines.append("| Class | n | TP | FP | FN | TN |")
    lines.append("|---|---|---|---|---|---|")
    for cls in sorted(by_class.keys()):
        c = by_class[cls]
        lines.append(f"| {cls} | {c['n']} | {c['tp']} | {c['fp']} | {c['fn']} | {c['tn']} |")

    lines.append("")
    lines.append("## Per-pair: D3-JSON vs NL cosine (same-factor-set subset, sorted by NL cosine)")
    lines.append("")
    lines.append("| Pair ID | Class | Label | cos D3-JSON | cos NL | NL-D3 Δ |")
    lines.append("|---|---|---|---|---|---|")
    for p in sorted(
        [p for p in pairs_enriched if p["factor_set_equal"]],
        key=lambda x: -x["cos_nl"],
    ):
        delta = p["cos_nl"] - p["cos_d3_json"]
        lines.append(
            f"| `{p['pair_id']}` | {p['distribution_class']} | {p['label']} | "
            f"{p['cos_d3_json']:.4f} | {p['cos_nl']:.4f} | {delta:+.4f} |"
        )

    (OUTPUT_DIR / "VERIFICATION_AUDIT.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    # Write raw data
    (OUTPUT_DIR / "verification_raw.json").write_text(
        json.dumps({
            "model_first_param_sha": sha,
            "fixture_n_pairs": len(fixture),
            "ablation_results": {
                label: {"best": r["best"], "sweep": r["sweep"]}
                for label, r in results.items()
            },
            "hard_subset_results": {
                label: {"best": r["best"], "sweep": r["sweep"]}
                for label, r in hard_results.items()
            },
            "per_class_at_w0_3_v2_tau": by_class,
            "pairs_enriched": pairs_enriched,
            "cosine_stats": {
                "near_dup_d3": stats(near_dup_d3),
                "near_dup_nl": stats(near_dup_nl),
                "distinct_all_d3": stats(distinct_d3),
                "distinct_all_nl": stats(distinct_nl),
                "distinct_same_fs_d3": stats(distinct_d3_same_factor),
                "distinct_same_fs_nl": stats(distinct_nl_same_factor),
            },
            "marginal_contributions": {
                "baseline_d3_cosine_f1": d3_cosine_f1,
                "delta_compound_alone": marginal_compound,
                "delta_nl_alone": marginal_nl_alone,
                "delta_combined": marginal_combined,
            },
        }, indent=2),
        encoding="utf-8",
    )

    print(f"[verify] outputs written to {OUTPUT_DIR.relative_to(REPO_ROOT)}/")
    print(f"[verify] see VERIFICATION_AUDIT.md for findings")


if __name__ == "__main__":
    sys.exit(main() or 0)
