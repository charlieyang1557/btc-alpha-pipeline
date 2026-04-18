# Phase 2B D7 Stage 1 — Sign-Off Notes

**Scope:** D7 Critic, Stage 1 deterministic sidecar  
**Branch:** `claude/setup-structure-validators-JNqoI`  
**Status at writing:** D7 Stage 1 notebook acceptance patched and passing; Stage 2 live critic work not started.  
**Active blueprint:** `blueprint/PHASE2_BLUEPRINT.md` (v2)

---

## 1. Purpose

This document records the Stage 1 sign-off notes, residual risks, and
frozen contracts for D7 Critic before any live critic backend is
introduced.

D7 Stage 1 did not evaluate critic quality. It verified that the Critic
can be inserted as a deterministic, fail-open sidecar without changing
D6 proposer behavior:

- D7a deterministic rule scoring is independently auditable.
- D7b is stubbed and obviously non-live.
- `run_critic()` never raises into the batch loop.
- `--with-critic=False` preserves the D6 output surface.
- `--with-critic=True` adds annotation only.
- The reliability fuse is scaffolded but not enforced.

This is an append-friendly sign-off note. Later D7 stages should add
new sections below rather than rewriting the Stage 1 record.

---

## 2. Stage 1 Sign-Off Verdict

D7 Stage 1 is accepted as a deterministic critic-sidecar integration.

The Phase 2B acceptance notebook now closes the main review gaps:

- Full `complexity_appropriateness` edge table is pinned in notebook
  section `AZ1`.
- Expanded D7a flag coverage is pinned in section `AZ2`.
- `run_critic()` 200-input never-raises fuzz is pinned in section `BB1`.
- D6 baseline preservation is audited in section `BD1` through a
  hard-coded pre-D7 key set plus canonical D6 behavior-surface
  byte-identity between critic-off and critic-on dry runs.

The accepted interpretation is:

> D7 Stage 1 inserts a deterministic, fail-open observer. It does not
> become a controller, does not alter proposer state, and does not
> change D6 lifecycle/accounting semantics.

---

## 3. Spec Defect D7-LP-1

**Issue:** The D7 launch prompt edge table listed:

```text
n_conditions = 3
n_factors    = 8
desc_len     = 600
expected     = 0.7225
```

This table value conflicts with the formula in the same spec.

The implemented and tested formula is:

```text
base = 1.0
if n_factors > 7:
    base *= 0.85
if desc_len > 500:
    base *= 0.9

1.0 * 0.85 * 0.9 = 0.765
```

The value `0.7225` would require the long-description penalty to be
`base *= 0.85` instead of `base *= 0.9`.

**Resolution:** Formula is canonical; the table row was wrong.

Implementation, unit tests, and notebook section `AZ1` all pin the
stacked-penalty row at `0.765`.

**Follow-up:** Update or annotate the original launch prompt / design
notes if they are preserved anywhere outside this closeout document, so
future readers do not treat `0.7225` as an alternate contract.

---

## 4. Residual Baseline Risk

No pre-D7 Stage 2d stub golden artifact was built before D7 Stage 1
landed.

The accepted substitute is:

- A hard-coded pre-D7 expected top-level key set in the acceptance
  notebook, approximately 35 keys.
- A canonical D6 behavior-surface JSON built from deterministic
  behavioral fields only.
- Byte-identity of that canonical surface between critic-off and
  critic-on dry runs.
- Explicit exclusion of dynamic envelope fields such as `batch_id`,
  timestamps, and runtime duration.

In the patched notebook run, the canonical D6 surface was `14,078`
bytes for both critic-off and critic-on runs, and the byte strings were
identical.

This catches:

- D6 schema drift in critic-off mode.
- Any single-sided D6 behavior change caused by enabling the critic.
- Any accidental `critic_result` pollution when `with_critic=False`.

It does **not** catch:

- A hypothetical future symmetric drift where both critic-off and
  critic-on paths change in exactly the same D6-behavioral way.

**Accepted risk:** This is acceptable for Stage 1 because no golden
artifact existed before D7. If Stage 2 surfaces D6 behavior anomalies,
consider retroactively generating and checking in a golden dry-run
artifact at that point.

---

## 5. Synthetic Empty-Factor-Set Path

`D7EmptyDSL` in the acceptance notebook is a hand-rolled defensive test
fixture.

The current Pydantic DSL schema cannot produce an empty factor set from
real proposer output because:

- `entry` and `exit` require at least one group.
- each group requires at least one condition.
- each condition requires a registered factor.

Therefore:

- `empty_factor_set`
- `structural_novelty = None`
- `factor_set_prior_occurrences = None`

are defense-in-depth semantics, not production-reachable behavior under
the current schema.

**Preserve this property:** If the DSL schema ever permits empty
conditions or empty factor sets, the D7a empty-factor semantics are
already locked and must be treated as part of the D7 contract.

---

## 6. Frozen Surfaces Entering Stage 2

The following surfaces are frozen at D7 Stage 1 sign-off.

Changes require explicit D7 v2 scope, not incidental Stage 2 tuning.

### 6.1 CriticResult Schema

`CriticResult` is the persisted sidecar schema. Field renames or
semantic changes are breaking changes for downstream D8 policy work.

Important semantics:

- `critic_status` and `d7b_mode` are orthogonal.
- `None` score blocks mean unknown / unavailable due to error.
- `0.0` score values mean measured bad, not missing.
- `d7a_rule_flags` is always a list.

### 6.2 D7a Rule Formulas

The four D7a rule formulas are frozen:

- `theme_coherence`
- `structural_novelty`
- `default_momentum_fallback`
- `complexity_appropriateness`

The `complexity_appropriateness` edge table is pinned in notebook
section `AZ1`.

### 6.3 D7a Flag Taxonomy

The six D7a flags are frozen:

- `empty_factor_set`
- `thin_theme_momentum_bleed`
- `factor_set_in_top3_repeated`
- `theme_anchor_missing`
- `description_length_near_limit`
- `n_conditions_heavy`

Expanded flag coverage is pinned in notebook section `AZ2`, including
calendar and volatility OR-anchor behavior.

### 6.4 D7b Score Dimensions

The three D7b score axes are frozen:

- `semantic_plausibility`
- `semantic_theme_alignment`
- `structural_variant_risk`

`structural_variant_risk` is the only reverse-polarity axis:

```text
0.0 = low risk / structurally distinct
1.0 = high risk / shallow variant
```

All other score axes are normal-polarity:

```text
0.0 = bad
1.0 = good
```

D8 policy must preserve this distinction and must not aggregate
`structural_variant_risk` as if it were normal-polarity.

---

## 7. Open Items For Later D7 Stages

These are not Stage 1 blockers, but they should be revisited as live
critic stages proceed:

- Live D7b prompt wording and leakage audit.
- Semantic score stability methodology.
- Critic reliability fuse thresholds and enforcement timing.
- Whether `structural_variant_risk` correlates with real repeated
  factor-set patterns under live D7b.
- Whether a pre-D7 / critic-off dry-run golden artifact should be
  generated retroactively if D6 behavior anomalies appear.

