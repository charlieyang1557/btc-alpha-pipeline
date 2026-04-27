# PHASE2B_D7_STAGE2C_SIGNOFF

## 1. Metadata and artifact anchors

| Field | Value |
|---|---|
| Sign-off date | 2026-04-19 |
| Author | Charlie Yang |
| Stage name | D7 Stage 2c |
| Source batch UUID | `5cf76668-47d1-48d7-bd90-db06d31982ed` |
| Selection anchor commit | `b71ffd1` |
| Expectations commit | `9100be07db0c23b2ae2c527a3149fd70efbe8416` |
| Expectations commit timestamp | `2026-04-19T14:05:22Z` |
| Expectations SHA256 | `14aaefafa958eee29f771d3c0b49db317ce8dac0d7802fb447113924ea19d484` |
| `replay_candidates.json` SHA256 | `17254003cf93a958cebc0ad26671da59aa166ff8de8063f8eabb503517aad49d` |
| `stage2c_batch_record.json` SHA256 | `c4a4072f61326dc23ba5d09c6263b5db5a0c08d2737dba8ccbdb5259a7823c3d` |
| Valid fire start | `2026-04-19T14:25:43.024994Z` |
| Valid fire end | `2026-04-19T14:30:32.601469Z` |
| Valid record write completion | `2026-04-19T14:30:32.602193Z` |
| Attempt 1 status | Aborted before evidence generation due to client-side auth failure |
| Attempt 1 archive | `raw_payloads/batch_5cf76668-47d1-48d7-bd90-db06d31982ed/critic/abort_attempt_1_auth_failure/` |
| Valid scientific run | Attempt 2 |

Attempt 1 began at `2026-04-19T14:05:46.158427Z` and aborted at
`2026-04-19T14:05:51.681449Z` after two `api_level` errors. No D7b
semantic judgments, scores, or reasoning were produced. The attempt was
archived rather than overwritten. Attempt 2 is the valid evidentiary run.

## 2. Executive summary

- Stage 2c was operationally valid and scientifically informative: 20/20 calls completed, all calls returned `critic_status="ok"`, and total actual cost was `$0.315765`, below the `$0.50` cap.
- The anti-hindsight anchor was preserved through the auth-abort and re-fire: expectations commit `9100be07db0c23b2ae2c527a3149fd70efbe8416` remained unchanged, with SHA256 `14aaefafa958eee29f771d3c0b49db317ce8dac0d7802fb447113924ea19d484`.
- The agreement axis was confirmed mechanically: 8/8 `agreement_expected` candidates had `structural_variant_risk >= 0.5`.
- The divergence axis failed mechanically: 0/3 `divergence_expected` candidates had `structural_variant_risk < 0.5`. This replicated the Stage 2b contradiction pattern on the overlap divergence cases.
- The neutral aggregate claim was falsified on the median condition: observed neutral median SVR was `0.85`, outside the pre-registered `[0.45, 0.70]` interval.
- Stage 2c revealed a low-SVR RSI-absent volatility-regime subpattern: C16/position 138 had SVR `0.30`, and C17/position 143 had SVR `0.15`.

The run succeeded operationally. Some important scientific claims failed.
That asymmetry is the intended use of the preregistration, not a defect in
the run.

## 3. Anti-hindsight integrity and rerun handling

### Operational validity

The valid Stage 2c run completed all 20 planned live D7b calls. The fire
script wrote `docs/d7_stage2c/stage2c_batch_record.json`, all 20 per-call
records, and all 20 prompt / response / critic-result raw payload triplets.
The run did not abort.

### Audit integrity

The expectations file was committed before the valid fire:

- Expectations commit: `9100be07db0c23b2ae2c527a3149fd70efbe8416`
- Expectations commit timestamp: `2026-04-19T14:05:22Z`
- Valid fire start: `2026-04-19T14:25:43.024994Z`
- Expectations SHA256 at fire: `14aaefafa958eee29f771d3c0b49db317ce8dac0d7802fb447113924ea19d484`

No `git commit --amend` was used after the expectations commit. The
expectations hash remained unchanged before re-fire. Attempt 1 was archived
under `abort_attempt_1_auth_failure/`; it did not generate semantic
evidence and therefore did not expose any D7b judgments before the valid
run.

### Scientific interpretability

Attempt 1 is an infrastructure abort. It does not provide evidence for or
against any Stage 2c candidate. Attempt 2 is the valid scientific run. The
evidence in this memo is drawn from Attempt 2 only, with Attempt 1 retained
for auditability.

## 4. Mechanical execution gates

| Gate | Evidence | Verdict |
|---|---:|---|
| Planned calls completed | `completed_call_count = 20 / 20` | PASS |
| Sequence abort | `sequence_aborted = false`, `abort_reason = null` | PASS |
| D7b error rate | `0 / 20` errors | PASS |
| Critic statuses | 20 `ok`, 0 `d7b_error` | PASS |
| Total cost | `$0.315765 < $0.50` | PASS |
| Per-call cost ceiling | max per-call cost `$0.019452 < $0.05` | PASS |
| Reasoning length | min `960`, max `1245`, all > 100 chars | PASS |
| Per-call records | 20 files present: `call_1_live_call_record.json` through `call_20_live_call_record.json` | PASS |
| Raw payloads | 20 prompt / response / critic-result triplets present under `raw_payloads/.../critic/` | PASS |
| Ledger rows | 20 re-fire rows reconciled inside fire timestamp window | PASS |
| Stage 2b archive | prompt / response / critic-result triplets preserved for positions 17, 73, 74, 97, 138 | PASS |
| Hashes logged | selection, expectations, prompt template, and batch record hashes recorded | PASS |

Operational sign-off: **PASS**.

## 5. Pre-registered claim adjudication

### 5.1 Agreement/divergence directional claims

Pre-registered rule:

- `agreement_expected`: D7b `structural_variant_risk >= 0.5`
- `divergence_expected`: D7b `structural_variant_risk < 0.5`

Observed:

| Axis | Positions | Expected side | Observed SVR values | Pass count | Verdict |
|---|---|---|---|---:|---|
| Agreement | 27, 97, 102, 107, 112, 147, 152, 162 | `>= 0.5` | 0.85, 0.95, 0.95, 0.95, 0.85, 0.95, 0.95, 0.90 | 8/8 | CONFIRMED |
| Divergence | 17, 73, 74 | `< 0.5` | 0.85, 0.95, 0.75 | 0/3 | FALSIFIED |

The broader selector-polarity claim did not replicate. Agreement labels
aligned with D7b semantic SVR, but divergence labels were again contradicted
in every case. This is not a full failure of Stage 2c. It is a failure of
the claim that SVR generally tracks the agreement/divergence selector label.

### 5.2 Overall 7/11 directional threshold

The pre-registered operational bar was:

- 11 directional candidates total.
- Overall consistency rate `observed_consistent_with_label == true` expected to be at least `7 / 11`.

Observed:

- Agreement candidates passing: `8 / 8`
- Divergence candidates passing: `0 / 3`
- Overall directional pass count: `8 / 11`

The operational threshold passed. This threshold pass should not be
confused with replication of the stronger selector-polarity claim, because
all three divergence cases failed in the same direction.

### 5.3 Neutral aggregate claim

Pre-registered neutral aggregate claim:

- median neutral SVR in `[0.45, 0.70]`
- at least 1 of 9 neutral scores below `0.5`
- at least 4 of 9 neutral scores at or above `0.5`

Observed neutral SVRs:

| Neutral positions | SVR values |
|---|---|
| 22, 32, 62, 72, 77, 83, 117, 138, 143 | 0.85, 0.90, 0.95, 0.75, 0.95, 0.75, 0.85, 0.30, 0.15 |

Observed aggregate:

| Condition | Observed | Verdict |
|---|---:|---|
| Median in `[0.45, 0.70]` | `0.85` | FAIL |
| At least 1 below `0.5` | `2` | PASS |
| At least 4 at or above `0.5` | `7` | PASS |

The neutral aggregate claim is **falsified on the median condition**. This
is a genuine pre-registered falsification and therefore epistemically
valuable. The observed neutral distribution was top-skewed, not centered
in the expected moderate-to-high interval.

### 5.4 Lock 10a overlap / test-retest claims

Five Stage 2b overlap candidates were included: positions 17, 73, 74, 97,
and 138.

| Position | Label | Stage 2b SVR | Stage 2c SVR | Threshold side preserved? | Drift |
|---:|---|---:|---:|---|---:|
| 17 | `divergence_expected` | 0.85 | 0.85 | yes, high/high | 0.00 |
| 73 | `divergence_expected` | 0.85 | 0.95 | yes, high/high | +0.10 |
| 74 | `divergence_expected` | 0.65 | 0.75 | yes, high/high | +0.10 |
| 97 | `agreement_expected` | 0.95 | 0.95 | yes, high/high | 0.00 |
| 138 | `neutral` | 0.15 | 0.30 | yes, low/low | +0.15 |

Directional preservation replicated: **5/5 pass**. The Stage 2b
contradiction pattern replicated on the overlap divergence cases: positions
17, 73, and 74 remained high-SVR despite `divergence_expected` labels.

The drift-direction sub-claim did not replicate. Where the expectations
allowed or anticipated modest downward drift for some overlap cases, the
observed changes were flat or upward. Directional preservation replicated;
drift-direction sub-claim failed.

## 6. Per-candidate outcome summary

Category rubric used for this table:

- `LOW`: `< 0.25`
- `MODERATE-LOW`: `0.25 <= SVR < 0.5`
- `MEDIUM`: expected middle category where specified in prose
- `MODERATE`: expected moderate category where specified in prose
- `MODERATE-HIGH`: high-side but not peak expectation
- `HIGH`: high / heavily recycled expectation

| Call | Pos | Label | Predicted SVR category | Observed SVR | Observed category | Threshold-side correct? | Major note |
|---:|---:|---|---|---:|---|---|---|
| 1 | 17 | `divergence_expected` | HIGH | 0.85 | HIGH | yes | Test-retest high-SVR contradiction replicated. |
| 2 | 22 | `neutral` | HIGH | 0.85 | HIGH | yes | Short-horizon MR near-repeat read as high SVR. |
| 3 | 27 | `agreement_expected` | MODERATE-HIGH | 0.85 | HIGH | yes | Agreement axis confirmed; stronger than predicted. |
| 4 | 32 | `neutral` | MODERATE | 0.90 | HIGH | yes | DSL awkwardness lowered plausibility but not SVR. |
| 5 | 62 | `neutral` | MODERATE-HIGH | 0.95 | HIGH | yes | Horizon-mix MR variant scored peak-high SVR. |
| 6 | 72 | `neutral` | HIGH | 0.75 | MODERATE-HIGH | yes | High side preserved; exact tag lower than expected. |
| 7 | 73 | `divergence_expected` | MODERATE-HIGH | 0.95 | HIGH | yes | Divergence contradiction replicated and strengthened. |
| 8 | 74 | `divergence_expected` | MEDIUM | 0.75 | MODERATE-HIGH | yes | Volume-divergence contradiction replicated above threshold. |
| 9 | 77 | `neutral` | HIGH | 0.95 | HIGH | yes | Low plausibility did not prevent high SVR. |
| 10 | 83 | `neutral` | MODERATE-HIGH | 0.75 | MODERATE-HIGH | yes | Exact category match; hybrid vol-regime case. |
| 11 | 97 | `agreement_expected` | MODERATE-HIGH | 0.95 | HIGH | yes | Agreement overlap stayed near ceiling. |
| 12 | 102 | `agreement_expected` | HIGH | 0.95 | HIGH | yes | DSL inconsistency clipped plausibility, not SVR. |
| 13 | 107 | `agreement_expected` | HIGH | 0.95 | HIGH | yes | Agreement axis confirmed despite plausibility weakness. |
| 14 | 112 | `agreement_expected` | HIGH | 0.85 | HIGH | yes | Repeated MR factor set scored high. |
| 15 | 117 | `neutral` | MODERATE-HIGH | 0.85 | HIGH | yes | MACD exit novelty did not lower SVR below high side. |
| 16 | 138 | `neutral` | MODERATE-LOW | 0.30 | MODERATE-LOW | yes | Low-SVR overlap direction replicated. |
| 17 | 143 | `neutral` | MODERATE-HIGH | 0.15 | LOW | no | Biggest miss; low-SVR RSI-absent vol-regime pattern emerged. |
| 18 | 147 | `agreement_expected` | HIGH | 0.95 | HIGH | yes | Heavy recurrence produced high SVR. |
| 19 | 152 | `agreement_expected` | MODERATE-HIGH | 0.95 | HIGH | yes | Entry-grammar variant still scored peak-high SVR. |
| 20 | 162 | `agreement_expected` | MODERATE-HIGH | 0.90 | HIGH | yes | Quieter faster-repair variant still high SVR. |

Summary:

- Exact category matches: `9 / 20`
- Threshold-side consistency against candidate-level informal SVR leans: `19 / 20`
- Largest miss: C17 / position 143, predicted high-side but observed `LOW` (`0.15`)

## 7. Falsifications

The following falsifications are recorded without softening:

1. Neutral aggregate median claim falsified.

   The pre-registered median interval was `[0.45, 0.70]`. The observed
   neutral median was `0.85`. The lower-side and high-side count conditions
   passed, but the aggregate claim as written was falsified on the median
   condition.

2. Broader selector-polarity claim did not replicate.

   The agreement axis passed 8/8, but the divergence axis passed 0/3. This
   means the selector-polarity claim does not hold as a general rule across
   the Stage 2c directional set.

3. Downward-drift expectation falsified.

   The overlap candidates preserved threshold side, but did not show the
   anticipated downward-drift tendency. The Stage 2c overlap changes were
   flat or upward: `0.00`, `+0.10`, `+0.10`, `0.00`, `+0.15`.

4. Several plausibility expectations were too optimistic.

   Sonnet penalized DSL awkwardness and upper-band/lower-band naming issues
   more strongly than several candidate-level prose predictions expected.
   Examples include C4 (`plaus=0.30`), C9 (`0.30`), C12 (`0.25`),
   C13 (`0.35`), C15 (`0.15`), C18 (`0.35`), and C19 (`0.25`).

These are not defects of the preregistration process; they are the point of
it. The value of Stage 2c comes from preserving which claims survived and
which failed under a locked fire.

## 8. New findings

### Low-SVR RSI-absent volatility-regime subpattern

The strongest new observation is the low-SVR RSI-absent volatility-regime
subpattern:

| Candidate | Position | Theme | Factors summary | Observed SVR |
|---:|---:|---|---|---:|
| 16 | 138 | `volatility_regime` | vol / volume / SMA / return, no RSI | 0.30 |
| 17 | 143 | `volatility_regime` | vol / volume / SMA / return horizons, no RSI | 0.15 |

This is a Stage 2c empirical observation and a candidate for Stage 2d
follow-up. It is not yet a universal rule: position 73 is also RSI-absent
and volatility-regime themed, but it retained high SVR. The narrower
pattern is the late vol / volume / SMA neighborhood without RSI-heavy
mean-reversion structure.

### Semantic SVR tracked recurrence/family history more than selector label

Sonnet's SVR judgments were more recurrence- and family-history-driven than
selector-label-driven. Agreement-labeled repeated MR candidates were high
SVR, but so were all three divergence-labeled overlap cases. This indicates
that the D7a selector label and D7b semantic SVR are not interchangeable
axes.

### Batch-internal similarity was not sufficient by itself

C16 and C17 were close in theme and factor neighborhood, yet C17 dropped to
SVR `0.15`. The result suggests that batch-internal similarity alone is
less predictive than the model's perceived prior-history structure and
factor-grammar interpretation.

## 9. Carry-forward constraints for Stage 2d

- Do not assume neutral distributions will center near moderate values; allow top-skew.
- Do not pre-commit a directional drift sign in overlap reruns unless directly supported.
- Treat RSI absence in volatility-regime candidates as a concrete factor to test, not just a prose intuition.
- Separate operational-identity variants from grammar-level or factor-set-level variants in future SVR prediction language.
- Continue distinguishing selector labels from semantic judgments rather than assuming they should align.
- Preserve explicit falsification accounting. Passing an operational threshold is not the same as confirming a scientific theory.

## 10. Final sign-off verdict

| Sign-off dimension | Verdict | Basis |
|---|---|---|
| Operational sign-off | PASS | 20/20 calls completed, no abort, 0 D7b errors, cost under cap |
| Audit / anti-hindsight sign-off | PASS | expectations committed pre-fire; hash unchanged through archived auth-abort and re-fire |
| Scientific sign-off | PASS WITH FALSIFICATIONS | valid evidence generated; multiple claims adjudicated, including failures |
| Broader selector-polarity claim | NOT REPLICATED | divergence axis 0/3 despite agreement axis 8/8 |
| Stage 2b contradiction-pattern replication | REPLICATED | all three overlap divergence cases remained high-SVR |
| Ready to advance to Stage 2d | YES | operationally valid run with auditable, interpretable outcomes |

Final statement: Stage 2c was operationally valid and scientifically
informative. It replicated the Stage 2b contradiction pattern on the
overlap divergence cases, confirmed the agreement axis, falsified the
pre-registered neutral median claim, and revealed a low-SVR RSI-absent
volatility-regime subpattern. It did not replicate the broader
selector-polarity claim that SVR tracks the agreement/divergence label.

The run succeeded. The data are usable. Some important claims failed. That
is still a scientific success because the failures are now anchored to a
pre-fire expectation file and preserved in the audit trail.

## Appendix A. Artifact hashes

| Artifact | SHA256 |
|---|---|
| `docs/d7_stage2c/replay_candidates.json` | `17254003cf93a958cebc0ad26671da59aa166ff8de8063f8eabb503517aad49d` |
| `docs/d7_stage2c/stage2c_expectations.md` | `14aaefafa958eee29f771d3c0b49db317ce8dac0d7802fb447113924ea19d484` |
| `docs/d7_stage2c/stage2c_batch_record.json` | `c4a4072f61326dc23ba5d09c6263b5db5a0c08d2737dba8ccbdb5259a7823c3d` |
| `docs/d7_stage2c/abort_attempt_1_log.md` | `26bd8079773b09f85476c5f468dd515231bcbae75000742c750d2c1682ec8ed8` |

## Appendix B. Attempt 1 abort summary

Attempt 1 produced two `d7b_error` records and then aborted under the
`api_level_consecutive` rule. The error was client-side authentication
configuration:

`TypeError: "Could not resolve authentication method. Expected either api_key or auth_token to be set..."`

No D7b semantic scores, reasoning, or response payloads were produced. The
attempt is preserved as operational history, not scientific evidence.

Preserved attempt-1 artifact hashes:

| Artifact | SHA256 |
|---|---|
| `stage2c_batch_record.json` | `0fb226d83732e5ba563541443d73f72d37f6c328d4566da0dc3ab6f8777c6076` |
| `call_1_live_call_record.json` | `9390f7e99e53783028916a3ad9e5a87b56181f80eb2e10eb15d566cce5049b29` |
| `call_2_live_call_record.json` | `bfb71a0e2c457fbfedb8d13e354cd2b3c9cc07ec8ba69672b549b50edb12bbb5` |

## Appendix C. Exact pre-registered claims adjudicated

The following claims were adjudicated as written:

- Agreement candidates predict `structural_variant_risk >= 0.5`.
- Divergence candidates predict `structural_variant_risk < 0.5`.
- Overall directional consistency threshold is at least `7 / 11`.
- Neutral candidates carry no per-candidate polarity prediction.
- Neutral aggregate median must fall in `[0.45, 0.70]`.
- Neutral aggregate must include at least 1 score below `0.5`.
- Neutral aggregate must include at least 4 scores at or above `0.5`.
- Stage 2b overlap candidates require explicit test-retest interpretation.

No failed claim is reinterpreted post hoc in this sign-off memo.
