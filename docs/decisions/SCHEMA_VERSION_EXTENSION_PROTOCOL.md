# Schema version extension protocol

> Canonical specification for **adding new artifact schema versions** to the
> per-domain tuple architecture sealed at T1.2 (commit `12dffde`). Uses
> `b_c_extended_v1` as the **reference exemplar** for a per-domain tuple +
> distinct validation helper + CONTRACT BOUNDARY discipline + heavy-private-impl
> extraction.
>
> Companion docs:
>
> - [B_C_EXTENDED_V1_SCHEMA_SPEC.md](./B_C_EXTENDED_V1_SCHEMA_SPEC.md) —
>   full schema spec for the `b_c_extended_v1` reference exemplar
>   (Contracts 2.0.1-2.0.5)
> - [WF_TEST_BOUNDARY_SEMANTICS.md](./WF_TEST_BOUNDARY_SEMANTICS.md) —
>   WF + evaluation domain semantics (pre-extension architecture)
> - [wf_test_boundary_semantics_test_classification.md](./wf_test_boundary_semantics_test_classification.md) —
>   test surface companion

---

## §0 Status + provenance

- **Status:** SEALED at T1.6 (this commit; sub-plan §2.6 deliverable `(f)`)
- **Scope:** extension protocol for adding new artifact schema versions to
  the per-domain tuple architecture; **NOT** authoritative on any specific
  schema version's field detail (companion docs own that)
- **Sealed source (sub-plan):**
  [`docs/superpowers/plans/2026-05-24-t1_6-documentation-consumer-enumeration-cycle-execution-plan.md`](../superpowers/plans/2026-05-24-t1_6-documentation-consumer-enumeration-cycle-execution-plan.md)
  §2.6 (T1.6 sub-plan v_final RATIFIED)
- **DS2 canonical doc location lock (T1.6 Charlie register 2026-05-24):**
  module docstring at [`backtest/wf_lineage.py`](../../backtest/wf_lineage.py)
  (brief summary + pointer to this doc) + this dedicated decisions/ doc
  (authoritative full protocol). Two-site pattern; this doc owns the
  protocol content; module docstring is the discoverable pointer.

---

## §1 Four-step extension protocol

> **PHASE 1 SKELETON (orchestrator):** structural outline + step headers + sub-step
> structure locked. **PHASE 2 (subagent fill):** detailed prose for each step
> + reference to `b_c_extended_v1` as worked exemplar.

### Step 1 — Identify attestation domain

Three existing domains:

1. **Evaluation** — single-run holdout artifacts
2. **Walk-forward (WF)** — walk-forward summary artifacts
3. **B-C-extended** — per-bar return series artifacts

If the new schema version belongs to one of the three existing domains, the
extension uses Step 2 + Step 3 only. If a **new domain** is required, the
extension MUST also add a new per-domain tuple + new helper + new CONTRACT
BOUNDARY entry; document the CONTRACT BOUNDARY discipline for the new tuple
at module docstring + at the declaration site.

The first question to answer is: which attestation domain does the new schema version describe? Each domain corresponds to a distinct kind of artifact produced by a distinct class of engine runs. The **evaluation domain** covers single-run holdout artifacts (typically `holdout_summary.json` or equivalent per-run JSON files written by `scripts/run_phase2c_evaluation_gate.py` and its successors). The **walk-forward domain** covers WF summary artifacts (typically `walk_forward_summary.json` files written by the corrected-engine batch runners). The **B-C-extended domain** covers per-bar return series artifacts carrying `returns_per_bar_path`, `returns_per_bar_sha256`, `T_obs`, and the `γ3`/`γ4` moment fields introduced at T1.2.

If the new schema version's artifact is produced by the same engine path and carries the same kind of lineage fields as one of the three existing domains, assign it to that domain and proceed with Steps 2+3 only. If the new schema version requires a genuinely different field contract (different required fields, different validation semantics, or a different producer/consumer boundary), a **new domain** must be created: this requires a new per-domain tuple, a new `check_*_semantics_or_raise()` helper, and a new CONTRACT BOUNDARY declaration at both the module docstring in `wf_lineage.py` and the tuple declaration site. Heavy-private-impl extraction (Step 4) should also be considered at that point.

The `b_c_extended_v1` addition at T1.2 is the canonical worked example of **new-domain creation**. Prior to T1.2, only two domains existed (evaluation + WF). The B-C-extended Scope-B cycle required preserving per-bar return series for moment estimation (`γ3`, `γ4`, `T_obs`) alongside the existing run-level summary fields — a fundamentally different artifact structure that neither existing domain's helper could validate correctly. Therefore, T1.2 Sub-decision A established a third domain with its own per-domain tuple (`ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS`), its own helper (`check_b_c_extended_semantics_or_raise`), and its own CONTRACT BOUNDARY declaration — rather than shoehorning `b_c_extended_v1` into `ACCEPTED_EVALUATION_SCHEMA_VERSIONS` or `ACCEPTED_WF_SCHEMA_VERSIONS`.

### Step 2 — Define new schema version constant at the domain's canonical declaration site

Canonical declaration site varies by domain:

- **Evaluation + WF domains:** [`backtest/wf_lineage.py`](../../backtest/wf_lineage.py)
  constants section (e.g., `ARTIFACT_SCHEMA_VERSION_<NEW>`)
- **B-C-extended domain:** [`backtest/artifact_schema.py`](../../backtest/artifact_schema.py)
  (per heavy-private-impl extraction discipline; re-export shim from
  `wf_lineage.py`)

Schema version constants follow a consistent naming convention: `ARTIFACT_SCHEMA_VERSION_<DOMAIN_UPPER>` in `UPPER_SNAKE_CASE`, with the string literal value being a `lowercase_snake_case` identifier that matches the constant name's suffix. For example, [`backtest/artifact_schema.py:42`](../../backtest/artifact_schema.py#L42) declares `ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1 = "b_c_extended_v1"`, where the constant name suffix `B_C_EXTENDED_V1` maps directly to the string value `"b_c_extended_v1"`. This one-to-one correspondence is required so that grep searches for the string literal (`rg '"b_c_extended_v1"'`) find both the declaration site and every consumer call site without false negatives.

The declaration site for the constant depends on whether Step 4 (heavy-private-impl extraction) applies. For the **evaluation and WF domains**, constants live in [`backtest/wf_lineage.py`](../../backtest/wf_lineage.py) alongside their per-domain tuples: `ARTIFACT_SCHEMA_VERSION_PHASE2C_7_1` at `:93` and `ARTIFACT_SCHEMA_VERSION_PHASE2C_8_1` at `:103`. For the **B-C-extended domain**, the constant was extracted to [`backtest/artifact_schema.py:42`](../../backtest/artifact_schema.py#L42) as part of the C1-extract-pre-SEAL Charlie register (2026-05-22), and then re-exported via the shim at [`backtest/wf_lineage.py:554`](../../backtest/wf_lineage.py#L554) to preserve backward compatibility. If Step 4 extraction is applied to a future domain, declare the constant at the extracted canonical site and add it to the shim re-export block at `wf_lineage.py:546-563`.

### Step 3 — Extend per-domain tuple + helper (integral; two mandatory sub-steps)

Step 3 contains two mandatory sub-steps `3a` + `3b` that together constitute
one logical extension operation.

#### Step 3a — Append to domain-appropriate accepted-versions tuple

| Domain | Tuple | Declaration site |
|---|---|---|
| Evaluation | `ACCEPTED_EVALUATION_SCHEMA_VERSIONS` | [`backtest/wf_lineage.py:111-114`](../../backtest/wf_lineage.py#L111-L114) |
| WF | `ACCEPTED_WF_SCHEMA_VERSIONS` | [`backtest/wf_lineage.py:119-122`](../../backtest/wf_lineage.py#L119-L122) |
| B-C-extended | `ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS` | [`backtest/artifact_schema.py:45-47`](../../backtest/artifact_schema.py#L45-L47) |

**CRITICAL — DO NOT append to legacy alias** `ACCEPTED_ARTIFACT_SCHEMA_VERSIONS`
at [`backtest/wf_lineage.py:129-132`](../../backtest/wf_lineage.py#L129-L132).
This is the backward-compat legacy alias of pre-domain-split tuple contents;
CONTRACT BOUNDARY explicitly forbids adding `b_c_extended_v1` or other
new-domain versions to it.

For `b_c_extended_v1`, the B-C-extended domain tuple did not exist prior to T1.2; there was no pre-existing `ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS` to append to. The T1.2 SEAL bundle (`12dffde`) created the tuple from scratch at [`backtest/artifact_schema.py:45-47`](../../backtest/artifact_schema.py#L45-L47):

```python
ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS: tuple[str, ...] = (
    ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1,
)
```

Before T1.2, the only accepted-versions tuple was the pre-split `ACCEPTED_ARTIFACT_SCHEMA_VERSIONS` (at `wf_lineage.py:129-132` post-split), which contained only evaluation/WF schema versions. The `b_c_extended_v1` constant was never added there — it would have violated the CONTRACT BOUNDARY by placing a B-C-extended schema version into the evaluation/WF union. A future implementer adding a second B-C-extended schema version (e.g., `b_c_extended_v2`) would append to `ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS` at `artifact_schema.py:45-47`, not to either of the evaluation or WF tuples. The legacy alias at `wf_lineage.py:129-132` remains frozen at its pre-split contents and MUST NOT receive any new entries.

#### Step 3b — Extend (or add) distinct `check_*_semantics_or_raise()` helper

Each helper enforces per-version field discipline at the helper site and
accepts ONLY its own domain's tuple per CONTRACT BOUNDARY.

When a new schema version belongs to an **existing domain**, Step 3b typically extends the existing helper with a new branch: append the new constant to the existing tuple (Step 3a) and add a new conditional block inside the existing `check_*_semantics_or_raise()` function that activates when `artifact_schema_version` equals the new constant. The `check_evaluation_semantics_or_raise()` helper at [`backtest/wf_lineage.py:352`](../../backtest/wf_lineage.py#L352) illustrates this pattern: it handles both `phase2c_7_1` and `phase2c_8_1` within a single function via the schema discriminator routing at `:486-503`.

When a new schema version establishes a **new domain** (the `b_c_extended_v1` case), Step 3b creates an entirely new helper. The new helper must (a) accept only its own domain's per-domain tuple in its version gate, (b) enforce field discipline specific to its domain's artifact contract, and (c) reject artifacts whose `artifact_schema_version` is absent or belongs to a different domain. For `b_c_extended_v1`, this resulted in [`check_b_c_extended_semantics_or_raise()` at `backtest/artifact_schema.py:654`](../../backtest/artifact_schema.py#L654), which implements a B1-c hybrid validation order (fail-fast Phase 1 on structural failures + collect-all Phase 2 on per-field failures) entirely distinct from the evaluation/WF helpers. The helper validates against `ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS` only and will never accept `phase2c_7_1` or `phase2c_8_1` values — enforcing the CONTRACT BOUNDARY at runtime rather than relying solely on the code-level constant separation.

### Step 4 — Heavy-private-impl extraction (optional)

If the new schema version's validation logic is heavy (>200 lines + complex
field discipline), consider extraction to a dedicated module per the
[`backtest/artifact_schema.py`](../../backtest/artifact_schema.py) precedent.
Preserve the public surface via shim re-export from
[`backtest/wf_lineage.py:546-563`](../../backtest/wf_lineage.py#L546-L563).

The **C1-extract-pre-SEAL Charlie register precedent** (2026-05-22) provides
the governance template for when to extract.

**IMPORTANT:** the extracted canonical site has its OWN CONTRACT GAPs (e.g.,
`b_c_extended_v1` has 3 GAPs in `artifact_schema.py` at lines 684 + 692 +
972 — see §3). Future implementers MUST enumerate canonical-site GAPs as part
of the extension protocol; do NOT default to `wf_lineage.py` GAPs alone
(per v2 PFR Advisor F3 fix-substantive-leak discipline).

Extraction is warranted when the validation block for a new schema version would push `wf_lineage.py` significantly beyond 800 lines or introduces complex per-field discipline (multi-phase validation order, SHA256 streaming, per-bar artifact file-existence checks, path confinement logic) that would make the module difficult to maintain. The informal threshold is: if the new helper + its constants + supporting private functions exceeds ~200 lines, extraction to a dedicated module is the preferred approach. Inline implementations that fit within ~50-100 lines can remain in `wf_lineage.py` directly.

The `b_c_extended_v1` extraction case was triggered at the C1-extract-pre-SEAL Charlie register (2026-05-22) immediately before T1.2 SEAL ratify. The B-C-extended validation block — `check_b_c_extended_semantics_or_raise()`, its supporting private helpers (`_validate_per_bar_artifact()`, `check_returns_path_confinement()`), the `BCExtendedSchemaValidationError` class, `LineageContext` dataclass, `canonicalize_execution_config_path()`, and `COST_ANCHOR_ID_MAPPING` — collectively exceeded 900 lines and warranted a dedicated module at [`backtest/artifact_schema.py`](../../backtest/artifact_schema.py). All public symbols were preserved for consumer backward compatibility via the re-export shim at [`backtest/wf_lineage.py:546-563`](../../backtest/wf_lineage.py#L546-L563):

```python
from backtest.artifact_schema import (  # noqa: E402
    ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1,
    ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS,
    COST_ANCHOR_ID_MAPPING,
    BCExtendedSchemaValidationError,
    check_b_c_extended_semantics_or_raise,
    canonicalize_execution_config_path,
    LineageContext,
)
```

After extraction, the canonical site for all CONTRACT GAP markers and future extension work is `artifact_schema.py`, not `wf_lineage.py`. Implementers must enumerate canonical-site GAPs (§3.2 pattern) in addition to `wf_lineage.py` GAPs when writing extension protocol documentation — missing canonical-site GAPs was the v2 PFR Advisor F3 substantive-leak catch during T1.6.

---

## §2 CONTRACT BOUNDARY (no cross-domain tuple pollution)

**Sealed module docstring at [`backtest/wf_lineage.py:47-51`](../../backtest/wf_lineage.py#L47-L51):**

```
CONTRACT BOUNDARY: ACCEPTED_EVALUATION_SCHEMA_VERSIONS and
ACCEPTED_WF_SCHEMA_VERSIONS are the existing-domain tuples; they MUST NOT
include b_c_extended_v1. ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS is the
B-C-extended-domain tuple; it MUST NOT include phase2c_7_1 or phase2c_8_1.
Each check_*_semantics_or_raise helper accepts ONLY its own domain's tuple.
```

**Reinforced at declaration site
[`backtest/wf_lineage.py:107-108`](../../backtest/wf_lineage.py#L107-L108):**

```
# CONTRACT BOUNDARY: no tuple may contain another domain's schema version.
# See module-level docstring for CONTRACT BOUNDARY declaration.
```

The CONTRACT BOUNDARY exists because Python's type system cannot enforce domain membership at the tuple level. All three per-domain tuples have the identical declared type `tuple[str, ...]`; there is no subtype distinction between `ACCEPTED_EVALUATION_SCHEMA_VERSIONS`, `ACCEPTED_WF_SCHEMA_VERSIONS`, and `ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS` from the type checker's perspective. A programmer adding a new schema version constant could silently append it to the wrong domain's tuple — for example, adding `"b_c_extended_v1"` to `ACCEPTED_EVALUATION_SCHEMA_VERSIONS` — and neither `mypy` nor `pyright` would flag the error. The string value would simply become a member of both tuples.

The failure mode this BOUNDARY prevents is **silent cross-domain validation acceptance**: if `b_c_extended_v1` were present in `ACCEPTED_EVALUATION_SCHEMA_VERSIONS`, then `check_evaluation_semantics_or_raise()` would accept B-C-extended per-bar artifacts as valid single-run holdout artifacts. These two artifact types carry entirely different required fields — a B-C-extended artifact has `returns_per_bar_path`, `T_obs`, `γ3`, `γ4` where a single-run holdout artifact has `evaluation_semantics`, `engine_commit`, `lineage_check`. The cross-domain acceptance would produce a misleading "validated" result on an artifact that lacks the fields the consuming code actually expects, with the error surfacing only at downstream attribute access rather than at the validation boundary.

The constant-level domain fence provides the only available enforcement mechanism given the type system gap. By declaring the BOUNDARY explicitly at both the module docstring ([`backtest/wf_lineage.py:47-51`](../../backtest/wf_lineage.py#L47-L51)) and the declaration site ([`backtest/wf_lineage.py:107-108`](../../backtest/wf_lineage.py#L107-L108)), future implementers are alerted at the exact code site where the violation could occur — making the constraint visible during code review and grep audits rather than discoverable only at runtime.

---

## §3 Six §2.6-scoped CONTRACT GAPs

Six CONTRACT GAPs scope-qualified per v6 SEAL-eve Round 1b Codex F3 LOW —
extension-protocol/code-surface only; T1.5 test-side CONTRACT GAP markers at
`tests/test_t1_5_smoke_end_to_end.py:21/95/126/179/379/392` are
OUT-OF-SCOPE for §2.6 extension protocol per T1.5 SEAL artifact authoritative.

### §3.1 GAPs in `backtest/wf_lineage.py` (3 GAPs)

| # | Line | GAP text | Forward-trigger semantic |
|---|---|---|---|
| 1 | [:117-118](../../backtest/wf_lineage.py#L117-L118) | "CONTRACT GAP: if a new WF-specific schema version is introduced, add it here and update `check_wf_semantics_or_raise`'s branching." | Step 3 trigger for WF tuple-append |
| 2 | [:126-128](../../backtest/wf_lineage.py#L126-L128) | "CONTRACT GAP: consumers that imported `ACCEPTED_ARTIFACT_SCHEMA_VERSIONS` and perform per-version branching should migrate to the per-domain tuple that matches their attestation domain. Audit via: `rg "ACCEPTED_ARTIFACT_SCHEMA_VERSIONS"`." | §2.7 consumer-audit trigger at each extension |
| 3 | [:281](../../backtest/wf_lineage.py#L281) | "CONTRACT GAP: regime_key validation against REGIME_KEY_LABEL_MAPPING." | Distinct from extension-boundary gaps; documented for completeness |

### §3.2 GAPs in `backtest/artifact_schema.py` (3 GAPs)

Added per v2 PFR Advisor F3 fix-substantive-leak catch; deferral direction
clarified per v3 PFR Advisor F4. These three GAPs were missed at v1 BLOCKING
F1 restructure (which moved the canonical site correctly but did not
enumerate canonical-site GAPs) — surfaced by v2 PFR cross-leg adversarial
review.

| # | Line | GAP text (paraphrased) | Direction |
|---|---|---|---|
| 4 | [:684](../../backtest/artifact_schema.py#L684) | "CONTRACT GAP: regime_key validation against REGIME_KEY_LABEL_MAPPING is deferred..." (in `check_b_c_extended_semantics_or_raise` docstring) | B-C-extended domain regime_key validation asymmetry; sibling to wf_lineage.py:281 |
| 5 | [:692](../../backtest/artifact_schema.py#L692) | "CONTRACT GAP: execution_config_path canonicalization is deferred to T1.3 engine `_write_to_registry()`..." | Deferred FROM consumer-side helper TO producer-side `engine._write_to_registry()` — consumer accepts canonicalized paths; producer canonicalizes before write |
| 6 | [:972](../../backtest/artifact_schema.py#L972) | "CONTRACT GAP: execution_config_path canonicalization (T1.3 engine..." | Sibling helper canonicalization deferral; same FROM consumer TO producer direction |

**Verbatim GAP text extracted from sealed code (Mode A verified):**

**GAP #1** — [`backtest/wf_lineage.py:117-118`](../../backtest/wf_lineage.py#L117-L118):
> `CONTRACT GAP: if a new WF-specific schema version is introduced, add it here and update check_wf_semantics_or_raise's branching.`

This GAP fires when a new artifact schema version belongs to the WF attestation domain. It triggers Step 3a (append to `ACCEPTED_WF_SCHEMA_VERSIONS`) AND a corresponding branch update inside `check_wf_semantics_or_raise()` for any new per-field validation that the new WF version requires.

**GAP #2** — [`backtest/wf_lineage.py:126-128`](../../backtest/wf_lineage.py#L126-L128):
> `CONTRACT GAP: consumers that imported ACCEPTED_ARTIFACT_SCHEMA_VERSIONS and perform per-version branching should migrate to the per-domain tuple that matches their attestation domain. Audit via: rg "ACCEPTED_ARTIFACT_SCHEMA_VERSIONS"`

This GAP fires at every extension cycle. Whenever a new schema version is added to any domain, the consumer audit is required: run `rg "ACCEPTED_ARTIFACT_SCHEMA_VERSIONS"` to find consumers still using the legacy alias, determine which domain each consumer belongs to, and migrate them to the appropriate per-domain tuple.

**GAP #3** — [`backtest/wf_lineage.py:281-284`](../../backtest/wf_lineage.py#L281-L284) (inside `check_wf_semantics_or_raise` docstring):
> `CONTRACT GAP: regime_key validation against REGIME_KEY_LABEL_MAPPING is deferred to a separate Charlie register-event per anti-pre-emption discipline. The new schema-version domain fence (FIX-B2) is the only per-version branching added here; regime_key is accepted as any non-empty string at this time.`

This GAP fires when regime_key validation is needed for WF artifacts. It is a sibling to GAP #4 in `artifact_schema.py`; the asymmetry between WF and evaluation-domain helpers (the latter validates `regime_key` against `REGIME_KEY_LABEL_MAPPING`) is intentional at T1.2 and must be resolved at a separate register-event.

**GAP #4** — [`backtest/artifact_schema.py:684-690`](../../backtest/artifact_schema.py#L684-L690) (inside `check_b_c_extended_semantics_or_raise` docstring):
> `CONTRACT GAP: regime_key validation against REGIME_KEY_LABEL_MAPPING is deferred. This helper accepts any non-empty string for regime_key. The sibling helper check_evaluation_semantics_or_raise validates regime_key against REGIME_KEY_LABEL_MAPPING; this asymmetry is intentional at T1.2 and must be resolved at a separate register-event per anti-pre-emption discipline. Trigger condition: when regime_key validation is needed for b_c_extended_v1 artifacts, add the check here and update this marker.`

This GAP fires when regime_key validation is required for B-C-extended per-bar artifacts. Adding the check requires both a code change to `check_b_c_extended_semantics_or_raise()` and an update to remove or replace this marker at the declaration site.

**GAP #5** — [`backtest/artifact_schema.py:692-699`](../../backtest/artifact_schema.py#L692-L699) (inside `check_b_c_extended_semantics_or_raise` docstring):
> `CONTRACT GAP: execution_config_path canonicalization is deferred to T1.3 engine _write_to_registry(). This helper accepts already-canonicalized execution_config_path from the artifact header. The canonicalization rule (repo_root commonpath containment + relpath + POSIX) belongs to the producer side (T1.3 engine). If a non-canonical path is passed here, the COST_ANCHOR_ID_MAPPING lookup fails closed (defensive). Trigger condition: when T1.3 engine is modified to write execution_config_path, add canonicalization there and add a corresponding test in T1.3's test file.`

This GAP fires when the T1.3 engine `_write_to_registry()` is modified to write `execution_config_path` into artifact headers. The canonicalization must be applied at the producer side (engine write boundary), not at the consumer-side validation helper.

**GAP #6** — [`backtest/artifact_schema.py:972-975`](../../backtest/artifact_schema.py#L972-L975) (inside `_validate_per_bar_artifact()` docstring):
> `CONTRACT GAP: execution_config_path canonicalization (T1.3 engine _write_to_registry() responsibility) is not performed here. The helper accepts already-canonicalized paths from the artifact header; non-canonical paths fail closed via mapping miss. See COST_ANCHOR_ID_MAPPING docstring.`

This is a sibling marker to GAP #5 at the private helper level. Both GAP #5 and GAP #6 document the same deferred canonicalization from the producer side; GAP #5 appears in the public-facing docstring while GAP #6 appears in the private `_validate_per_bar_artifact()` helper that actually performs the `COST_ANCHOR_ID_MAPPING` lookup.

### §3.3 Stale upstream authority — docstring at `wf_lineage.py:386-389` (per v3 PFR Codex F1)

The docstring at [`backtest/wf_lineage.py:386-392`](../../backtest/wf_lineage.py#L386-L392)
was historically: *"Future arcs extend the branching by appending to
`ACCEPTED_ARTIFACT_SCHEMA_VERSIONS`."*

This is **stale text pre-dating T1.2 Sub-decision A per-domain split**;
sealed code at [`:490-492`](../../backtest/wf_lineage.py#L490-L492) actually
gates on `ACCEPTED_EVALUATION_SCHEMA_VERSIONS`, not the legacy union. Parent
plan v5 §2.0.2 line 76 contains analogous stale wording.

**T1.6 update applied** (per §2.6.4 PASS criterion 10): docstring updated to
per-domain tuple wording with pointer to this protocol doc. See §1 Step 3a
for the correct procedure.

**Parent plan v5 §2.0.2 line 76 qualification** (per §2.6.4 PASS criterion 11):
the legacy cite is "superseded by T1.2 Sub-decision A per-domain split per
Sub-decision A lock; cite preserved for historical context but DO NOT follow
as live instruction."

---

## §4 `b_c_extended_v1` reference exemplar

- **Canonical implementation site:**
  [`check_b_c_extended_semantics_or_raise()` at `backtest/artifact_schema.py:654`](../../backtest/artifact_schema.py#L654)
- **Re-export shim:**
  [`backtest/wf_lineage.py:546-563`](../../backtest/wf_lineage.py#L546-L563)
  (preserves public surface; consumer backward compat per C1-extract-pre-SEAL
  Charlie register 2026-05-22)
- **T1.2 SEAL bundle:** `12dffde` (reference implementation commit)
- **Schema spec:** see [B_C_EXTENDED_V1_SCHEMA_SPEC.md](./B_C_EXTENDED_V1_SCHEMA_SPEC.md)
  §1-§4 for full field detail + 14-field header table + T_obs + per-bar
  validation discipline

**Step 1 — Domain identification:** The B-C-extended Scope-B cycle required artifact headers carrying per-bar return series linkage (`returns_per_bar_path`), per-bar file integrity (`returns_per_bar_sha256`), a count of finite observations (`T_obs`), and moment statistics (`γ3`, `γ4`). Neither the evaluation domain (single-run holdout summaries) nor the WF domain (walk-forward summaries) described this artifact type — both use run-level aggregate fields with no per-bar linkage. A **third domain** was required, establishing the B-C-extended domain with a distinct tuple, distinct helper, and distinct CONTRACT BOUNDARY declaration. Decision locked at T1.2 Sub-decision A (SEAL bundle `12dffde`, 2026-05-22).

**Step 2 — Constant declaration:** The constant `ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1 = "b_c_extended_v1"` was declared at [`backtest/artifact_schema.py:42`](../../backtest/artifact_schema.py#L42) (canonical extraction site). Because Step 4 extraction was applied simultaneously (see below), the constant was never declared in `wf_lineage.py` directly; it entered the public surface solely via the shim re-export. SEAL bundle: `12dffde`.

**Step 3a — New per-domain tuple:** `ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS` was created at [`backtest/artifact_schema.py:45-47`](../../backtest/artifact_schema.py#L45-L47) as a single-element tuple `(ARTIFACT_SCHEMA_VERSION_B_C_EXTENDED_V1,)`. The tuple was not appended to any pre-existing structure — it was freshly created as part of the T1.2 Sub-decision A per-domain split. SEAL bundle: `12dffde`.

**Step 3b — New helper:** `check_b_c_extended_semantics_or_raise()` was implemented at [`backtest/artifact_schema.py:654`](../../backtest/artifact_schema.py#L654). The helper enforces a B1-c hybrid validation order: Phase 1 (fail-fast on structural failures — missing `artifact_schema_version`, wrong domain, path-confinement violations) followed by Phase 2 (collect-all per-field failures using `BCExtendedSchemaValidationError` with a structured `errors` list). This two-phase pattern was chosen per Sub-decision B lock to provide both immediate structural rejection and comprehensive per-field diagnostics in a single call. SEAL bundle: `12dffde`.

**Step 4 — Heavy-private-impl extraction:** The C1-extract-pre-SEAL Charlie register (2026-05-22) identified that the full B-C-extended block — constants, mapping, `BCExtendedSchemaValidationError`, `canonicalize_execution_config_path()`, `LineageContext`, `check_b_c_extended_semantics_or_raise()`, `check_returns_path_confinement()`, and `_validate_per_bar_artifact()` — would exceed 900 lines in `wf_lineage.py`, violating the 800-line file-size guideline. The block was extracted to `backtest/artifact_schema.py` before the T1.2 SEAL ratify commit, and public symbols were made available to existing consumers via the re-export shim at [`backtest/wf_lineage.py:546-563`](../../backtest/wf_lineage.py#L546-L563). Consumer code using `from backtest.wf_lineage import check_b_c_extended_semantics_or_raise` required no changes. SEAL bundle: `12dffde` (T1.2 + T1.3 + T1.1 combined SEAL).

---

## §5 Validation logic routing

`artifact_schema_version` field routes validation via per-domain helper at
consumer call site. Consumer determines domain → calls domain-appropriate
helper → helper validates `artifact_schema_version` against its own domain's
tuple + rejects mismatched values.

The routing responsibility is **split between the consumer call site and the helper**: the consumer determines which domain the artifact belongs to (based on how the artifact was produced or where it was loaded from) and calls the domain-appropriate helper; the helper then validates the `artifact_schema_version` field against its own domain's tuple and rejects values from other domains or absent schema versions.

Concrete routing examples:

- **WF artifact** (loaded from `walk_forward_summary.json` produced by a batch runner): call `check_wf_semantics_or_raise(summary, artifact_path=path)`. This helper validates `wf_semantics`, `corrected_wf_semantics_commit`, and (when present) `artifact_schema_version` against `ACCEPTED_WF_SCHEMA_VERSIONS`. Passing `b_c_extended_v1` as `artifact_schema_version` will **raise** because `"b_c_extended_v1"` is not in `ACCEPTED_WF_SCHEMA_VERSIONS`.

- **Single-run holdout artifact** (loaded from `holdout_summary.json` produced by `run_phase2c_evaluation_gate.py`): call `check_evaluation_semantics_or_raise(summary, artifact_path=path)`. This helper validates the five legacy fields plus `regime_key`/`regime_label` when `artifact_schema_version` is present and in `ACCEPTED_EVALUATION_SCHEMA_VERSIONS`.

- **B-C-extended per-bar artifact** (loaded from a per-run header JSON carrying `returns_per_bar_path`): call `check_b_c_extended_semantics_or_raise(summary, artifact_path=path)`. This helper validates `artifact_schema_version` against `ACCEPTED_B_C_EXTENDED_SCHEMA_VERSIONS` (Phase 1) and then validates all 12 required string fields, `T_obs`, `parent_run_id`, cost anchor consistency, and per-bar file integrity (Phase 2).

The consumer must not infer domain from the artifact content (e.g., by checking whether `wf_semantics` is present) — that pattern creates implicit coupling between the routing logic and the field contract. Instead, domain is determined by the **producer code path** that wrote the artifact. Scripts that load artifacts from a known directory (e.g., `data/phase2c_evaluation_gate/`) can hard-code the domain; generic loaders should require the caller to specify the domain explicitly rather than auto-detecting it.

---

## §6 Forward-compatibility

Future cycles adding new schema versions follow the same 4-step protocol
(§1). Each extension carries two recurring obligations:

1. **Consumer audit obligation** per CONTRACT GAP at
   [`backtest/wf_lineage.py:126-128`](../../backtest/wf_lineage.py#L126-L128)
   — audit consumers of the legacy alias and the per-domain tuples at each
   extension via `rg` patterns enumerated in [B_C_EXTENDED_V1_SCHEMA_SPEC.md](./B_C_EXTENDED_V1_SCHEMA_SPEC.md)
   §3 consumer enumeration.
2. **Canonical-site GAP enumeration obligation** if heavy-private-impl
   extraction (Step 4) is applied — enumerate the extracted canonical site's
   OWN CONTRACT GAPs alongside `wf_lineage.py` GAPs (per v2 PFR Advisor F3
   fix-substantive-leak empirical).

Every future extension cycle must work through the following checklist. Items 1-4 are structural (required for all extensions); items 5-6 apply conditionally; item 7 is recurring at every extension regardless of domain:

1. **Domain identification** (Step 1): Determine whether the new schema version belongs to an existing domain or requires a new one. If a new domain is needed, create the per-domain tuple + helper + CONTRACT BOUNDARY declaration atomically in the same commit — a partial new-domain state (tuple without helper, or helper without BOUNDARY declaration) is never acceptable.

2. **Constant at canonical site** (Step 2): Declare the `ARTIFACT_SCHEMA_VERSION_<DOMAIN>_<REVISION>` constant at the canonical site (either `wf_lineage.py` for inline implementations or the extracted module for heavy-private-impl cases). Use `UPPER_SNAKE_CASE` with a `lowercase_snake_case` string literal value.

3. **Tuple append** (Step 3a): Append the new constant to the domain-appropriate per-domain tuple. Never append to the legacy alias `ACCEPTED_ARTIFACT_SCHEMA_VERSIONS` at `wf_lineage.py:129-132`. If the target domain is `artifact_schema.py`-hosted (B-C-extended), also add the shim re-export entry in the `wf_lineage.py:546-563` block for backward compatibility.

4. **Helper update or creation** (Step 3b): Either extend the existing domain helper with a new branch for the new schema version, or create a new helper for a new domain. New helpers must implement the B1-c hybrid validation pattern (fail-fast Phase 1 + collect-all Phase 2) per the `check_b_c_extended_semantics_or_raise()` precedent.

5. **Heavy-private-impl extraction** (Step 4, conditional): Apply if the new validation block would push `wf_lineage.py` beyond 800 lines or introduces complex multi-phase logic. Extract to a dedicated module, preserve the public surface via shim re-exports, and note the C1-extract-pre-SEAL Charlie register pattern as governance precedent.

6. **Canonical-site GAP enumeration** (conditional on Step 4): If Step 4 extraction is applied, enumerate all CONTRACT GAPs in the extracted canonical site's own module (not just in `wf_lineage.py`). Missing canonical-site GAPs was the T1.6 v2 PFR Advisor F3 substantive-leak catch — enumeration must be part of the extension protocol documentation, not an afterthought.

7. **Consumer audit** (recurring, every extension): Run `rg "ACCEPTED_ARTIFACT_SCHEMA_VERSIONS"` to find consumers still referencing the legacy alias. For each, determine which domain the consumer belongs to and migrate it to the appropriate per-domain tuple. This audit is required per CONTRACT GAP at [`backtest/wf_lineage.py:126-128`](../../backtest/wf_lineage.py#L126-L128) and the consumer enumeration discipline established at T1.6.

---

## §7 Cross-references

**Sealed source (sub-plan):**

- [`docs/superpowers/plans/2026-05-22-b_c_extended-scope_b-cycle-execution-plan.md`](../superpowers/plans/2026-05-22-b_c_extended-scope_b-cycle-execution-plan.md)
  §2.0.2 — Contract 2.0.2 schema version + distinct validation branch policy

**Companion docs:**

- [B_C_EXTENDED_V1_SCHEMA_SPEC.md](./B_C_EXTENDED_V1_SCHEMA_SPEC.md) — full
  spec for the reference exemplar (Contracts 2.0.1-2.0.5)
- [WF_TEST_BOUNDARY_SEMANTICS.md](./WF_TEST_BOUNDARY_SEMANTICS.md) — WF +
  evaluation domain semantics (pre-extension architecture)

**HARD CONSTRAINTS:**

- [`CLAUDE.md`](../../CLAUDE.md) Contract Markers section (L297-300) —
  CONTRACT GAP + CONTRACT BOUNDARY + DESIGN INVARIANT discipline

**Sealed implementation:**

- [`backtest/wf_lineage.py`](../../backtest/wf_lineage.py) — per-domain
  tuples + CONTRACT BOUNDARY + helpers + legacy alias + shim re-exports
- [`backtest/artifact_schema.py`](../../backtest/artifact_schema.py) —
  `b_c_extended_v1` canonical implementation (extracted module per C1
  Charlie register 2026-05-22)

**Reference SEAL bundles:**

- `12dffde` (2026-05-22) — T1.2 + T1.3 + T1.1 SEAL bundle (per-domain tuple
  split + helpers + LineageContext + writer chain)
- `b6da611` (2026-05-24) — T1.6 sub-plan v_final ratify
- (this commit) — T1.6 SEAL bundle (this doc + B_C_EXTENDED_V1_SCHEMA_SPEC.md
  + data_dictionary.md updates + consumer enumeration table)

**Cycle empirical (memory standing rules):**

- [`memory/feedback_invariant_level_vs_enumeration.md`](../../../.claude/projects/-Users-yutianyang-Documents-GitHub-btc-alpha-pipeline/memory/feedback_invariant_level_vs_enumeration.md)
  — invariant-level closure discipline (relevant to Step 4 extraction +
  canonical-site GAP enumeration)
