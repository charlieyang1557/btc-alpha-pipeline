# PHASE2C_6 Evaluation Gate Results

## 1. Scope and verdict

PHASE2C_6 executed cleanly and produced a load-bearing negative
selection-power finding: in this batch, corrected WF Sharpe > 0.5
did not enrich for 2022 holdout survival; audit-only candidates
survived at a higher rate (12/154, 7.79%) than primary candidates
(1/44, 2.27%).

This closeout reports results from three runs (smoke 4-candidate,
primary 44-candidate, audit 198-candidate) of the PHASE2C_6
evaluation gate against the corrected-engine batch
`b6fcbf86-4d57-4d1f-ae41-1778296b1ae9`. The evaluation gate is the
2022 regime holdout 4-criterion AND-gate (sharpe ≥ −0.5,
max_drawdown ≤ 0.25, total_return ≥ −0.15, total_trades ≥ 5;
inclusive inequalities) defined in `config/environments.yaml`.
Lineage discipline follows Section RS of
`docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md` for corrected-engine
consumption, using a separate single-run holdout attestation domain:
`evaluation_semantics='single_run_holdout_v1'`.

Coverage scope: 2022 regime holdout evaluation against the
corrected-engine batch's 198 candidates. Out of coverage scope:
DSR (Deflated Sharpe Ratio) computation, CPCV (Combinatorial
Purged Cross-Validation), MDS (Minimum Detectable Skill),
paper-trading evaluation, deployment-readiness evaluation, and
multi-regime holdout evaluation. The verdict is empirically
significant for PHASE2C_7+ scoping but does not establish
methodology-level conclusions; the bounds of the finding are
detailed in §6.

## 2. Artifact and lineage integrity

The PHASE2C_6 arc produced three run directories under
`data/phase2c_evaluation_gate/`:

- `smoke_v1/` — 4 candidates, plumbing verification (PHASE2C_6.3,
  commit `ca096ef`)
- `primary_v1/` — 44 candidates, primary universe (PHASE2C_6.4,
  commit `d6f481a`)
- `audit_v1/` — 198 candidates, audit universe (PHASE2C_6.5,
  commit `e6cecb9`)

All three runs ran against engine commit `eb1c87f` (corrected WF
engine, lineage tag `wf-corrected-v1`) and stamped each artifact
with: `evaluation_semantics='single_run_holdout_v1'`,
`engine_commit='eb1c87f'`,
`engine_corrected_lineage='wf-corrected-v1'`,
`lineage_check='passed'`,
and a non-empty `current_git_sha`. Per-artifact validation against
`check_evaluation_semantics_or_raise()` post-write produced 0
failures across all 246 run-level evaluations (4 + 44 + 198) and
3 aggregate run summaries. 0 holdout_error states were observed.

Per-candidate detail and the broader lineage chain (back to the
corrected engine commit and forward to the consumption guards
applied here) is covered in §4's lineage-integrity subsection;
this section names the artifact paths and confirms attestation
integrity without restating the per-candidate verification.

## 3. Primary universe result (1 of 44)

The primary universe consists of the 44 batch candidates with
`wf_test_period_sharpe > 0.5` per the corrected-engine canonical
artifacts. Each was evaluated against the 2022 regime holdout
4-criterion AND-gate (sharpe ≥ −0.5, max_drawdown ≤ 0.25,
total_return ≥ −0.15, total_trades ≥ 5; inclusive inequalities).

**Headline.** 1 of 44 candidates passed (2.27%). 43 failed; 0
holdout_error states. Wall-clock: 53.5s total at mean 1.21s per
candidate.

**Survivor.** `bf83ffec97485f47`, position 130 in the original batch,
theme `calendar_effect`, name `monday_weakness_tuesday_rebound_130`.
Walk-forward Sharpe 1.1381; 2022 holdout metrics: Sharpe +0.013751,
maximum drawdown 23.43%, total return −2.97%, 22 trades. The
holdout Sharpe is barely positive; the drawdown is within 1.6
percentage points of the 25% gate threshold and the return is
within 12 percentage points of the −15% gate threshold. The
candidate passes the gate as currently calibrated, but its
proximity to three of the four thresholds makes it a borderline
holdout survivor rather than a strong one.

**Failure-mode distribution.** Of the 43 failed candidates:

- 35 (81.4%) failed the drawdown criterion (max_drawdown > 0.25).
  Drawdown is the dominant failure mode — most failed candidates
  took meaningful directional exposure that compounded into deep
  drawdowns under sustained 2022 selling pressure.
- 28 (65.1%) failed the Sharpe criterion (sharpe < −0.5).
- 28 (65.1%) failed the return criterion (total_return < −0.15).
- 7 (16.3%) failed the trade-count criterion (total_trades < 5).
  Of these, 2 fired zero trades during 2022 and 5 fired 1–4 trades.

The Sharpe and return failures co-occur with drawdown failures in
most cases — a strategy that loses ≥15% of capital with ≥25%
drawdown necessarily produces a poor Sharpe. The trade-count
failures are a structurally distinct mode: strategies that fired
infrequently rather than performed badly.

**Rank-1 sanity check.** The corrected-engine batch's rank-1
candidate (`0bf34de1`, volume_divergence theme, walk-forward Sharpe
+2.789) failed the gate with only 2 trades in calendar 2022. A
2-trade outcome on 8,760 hourly bars warrants a sanity check
distinguishing real strategy behavior from pipeline artifact.
Inspection of the candidate's compiled DSL confirms the 2-trade
outcome is consistent with strategy logic: the entry condition is
a 4-way AND (`volume_zscore_24h > 1.5` AND `return_24h < −0.01`
AND `rsi_14 < 45` AND `close > sma_50`). The fourth conjunct
(`close > sma_50`) requires price to be above its 50-bar simple
moving average — a condition that was near-permanently false
during 2022's sustained downtrend. The strategy was designed to
fire on oversold-within-uptrend patterns, which 2022 did not
supply. The 2-trade outcome reflects regime structure, not
evaluation pipeline failure.

**Near-miss cluster.** Four failed candidates exhibited a
distinctive failure profile: positive 2022 holdout Sharpe with
in-bound drawdown and return, failing only on the trade-count
criterion:

- 06c3b4a2 (mean_reversion, hd_sh=+0.7113, 1 trade)
- d8e92ae4 (calendar_effect, hd_sh=+1.2624, 4 trades)
- e12477c9 (mean_reversion, hd_sh=+0.5317, 4 trades)
- b4dbd6c5 (volatility_regime, hd_sh=+0.8693, 1 trade)

These strategies generated profitable signals when they fired but
fired too infrequently to satisfy the n=5 minimum that the gate's
trades criterion enforces. The trades criterion exists to prevent
spurious low-sample passes (a single lucky trade producing
high-Sharpe statistics with no statistical basis); these four
candidates trip that criterion under the pre-registered gate logic
even though their in-sample 2022 behavior was favorable. Whether
such candidates warrant separate consideration is discussed in §9
as a question the trade-count threshold raises rather than
resolves.

## 4. Audit universe result (13 of 198)

The audit universe extends the primary evaluation to all 198 batch
candidates, including the 154 with `wf_test_period_sharpe <= 0.5`
that the primary criterion rejected. The audit universe answers a
question the primary universe alone cannot: does the corrected WF
gate enrich for 2022 holdout survival, or do rejected candidates
survive at comparable rates?

**Headline.** 13 of 198 candidates passed (6.57%). 185 failed; 0
holdout_error states. Wall-clock: 3 minutes 56.88 seconds total
at mean 1.20s per candidate. The 198-candidate population breaks
down as:

- Primary subset (`wf_test_period_sharpe > 0.5`, n=44): 1 passed
  (2.27%)
- Audit-only subset (`wf_test_period_sharpe <= 0.5`, n=154): 12
  passed (7.79%)

The audit-only pass rate (12/154 = 7.79%) exceeds the primary pass
rate (1/44 = 2.27%). The selection-power implication of this
comparison is the closeout's load-bearing finding and is treated
in §5.

**Sanity reproduction.** The 44-candidate primary subset within the
audit_v1 run reproduces the standalone primary_v1 run exactly. The
survivor identity is identical (`bf83ffec97485f47` in both runs).
The survivor's 2022 holdout Sharpe is bit-identical across runs
(`+0.013751` in primary_v1 CSV, `+0.013751` in audit_v1 CSV — string
match, not just float-precision match). The corrected engine is
deterministic across separate orchestration invocations: the same
candidate evaluated under the same input data and gate produces
the same downstream metric values regardless of whether the
evaluation runs in a 44-candidate or 198-candidate orchestration.

This reproducibility check matters for closeout integrity. If
primary_v1 and audit_v1's primary-subset rows had differed,
either (a) a non-deterministic component existed in the
orchestration pipeline, or (b) something in the evaluation
sequence (e.g., shared mutable state, ordering effects) was
introducing run-dependent drift. The bit-identical match rules
out both failure modes in this observed comparison.

**Survivor distribution by population.** Across all 13 survivors:

- 1 in primary universe (`bf83ffec`, the borderline survivor
  detailed in §3)
- 12 in audit-only — full enumeration in §7

Of the 13 survivors, 10 have `wf_test_period_sharpe <= 0`. The
survivor population is concentrated in WF-rejected candidates
rather than WF-accepted ones — a finding §5 treats as the
selection-power result.

**Lineage integrity.** All 198 per-candidate JSON artifacts and
the aggregate JSON were validated against
`check_evaluation_semantics_or_raise()` post-write. Every artifact
carries: `evaluation_semantics='single_run_holdout_v1'`,
`engine_commit='eb1c87f'`,
`engine_corrected_lineage='wf-corrected-v1'`,
`lineage_check='passed'`,
and a non-empty `current_git_sha`. The 198-candidate run is
within the corrected-engine lineage attestation and meets the
Section RS consumption discipline from
`docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md`.

## 5. Selection-power adjudication

The empirical comparison between the primary universe (corrected WF
winners with `wf_test_period_sharpe > 0.5`) and the audit-only
population (`wf_test_period_sharpe <= 0.5`) is the closeout's
load-bearing finding.

**Headline.** In this batch, corrected WF Sharpe > 0.5 did not
enrich for 2022 holdout survival. The audit-only pool survived at
a higher rate (12/154 = 7.79%) than the primary pool (1/44 = 2.27%).
The audit-only pass rate exceeds the primary pass rate by 5.52
percentage points; expressed as a ratio, audit-only candidates were
3.43× more likely to survive the 2022 regime holdout than primary
candidates within this batch.

Both metrics are sensitive to the small primary universe size
(n=44); a single additional primary survivor would shift the
gap to 3.24pp and the ratio to 1.71×. The finding's *direction*
(audit-only > primary) still holds at the current data, but its
*magnitude* should be read with the n=44 caveat in mind.

This is a stronger negative result than "the WF gate has weak
selection power." Selection power for 2022 robustness would require
the primary pool to enrich for survivors at a rate at least
comparable to the audit-only pool. Within this batch, the relationship
is inverted: the gate's selection process produced a population less
likely to survive the regime holdout than the candidates it rejected.

**Within-theme anti-selection (volume_divergence, momentum).** The
inversion is most acute when the two populations are compared within
theme rather than across all 198 candidates:

- volume_divergence: primary 0/12 (0%), audit-only 4/28 (14.3%)
- momentum: primary 0/3 (0%), audit-only 3/36 (8.3%)

Within these two themes, the WF gate produced zero 2022-survivors
while the rejected pool produced multiple. The within-theme view
isolates regime-fit effects from cross-theme distribution effects:
the comparison holds the alpha-thesis category constant, so the
inversion cannot be attributed to the primary pool simply being
weighted toward regime-incompatible themes. Within volume_divergence
and momentum specifically, the gate's selection process pushed away
from candidates that turned out to be 2022-robust.

**Audit survivors exceeding the primary survivor's holdout Sharpe.**
The primary universe's single survivor (`bf83ffec`) passed the
4-criterion gate with a borderline holdout Sharpe of +0.014. Within
the audit-only survivor cohort, 9 of 12 candidates have a higher
holdout Sharpe than the primary survivor:

- 18c2a5f7 (momentum, wf=−1.511 → hd_sh=+0.960)
- 7f296ee9 (calendar_effect, wf=−0.898 → hd_sh=+0.722)
- 1d6a587a (calendar_effect, wf=−0.203 → hd_sh=+0.586)
- 0845d1d7 (volume_divergence, wf=−0.072 → hd_sh=+0.508)
- 94b3d1fd (calendar_effect, wf=−0.192 → hd_sh=+0.479)
- ab7584d2 (volume_divergence, wf=−0.207 → hd_sh=+0.398)
- c200a95d (calendar_effect, wf=+0.196 → hd_sh=+0.355)
- f4977b3e (volume_divergence, wf=−0.753 → hd_sh=+0.347)
- 37c0661e (momentum, wf=−2.193 → hd_sh=+0.070)

Eight of the nine carry negative WF Sharpe. The candidate with the
highest 2022 holdout Sharpe in the entire batch (18c2a5f7,
hd_sh=+0.960) was rejected by the corrected WF gate at
wf_test_period_sharpe = −1.511 — a candidate the gate rated among
its worst.

Across all 13 survivors (1 primary + 12 audit-only), 10 of 13 have
`wf_test_period_sharpe <= 0`. The corrected WF metric, treated as a
ranking criterion for 2022 holdout survival, points the wrong way
within this batch.

**On mechanism.** The empirical observation is that the corrected WF
metric anti-selects against 2022-robust candidates within this batch;
the mechanism producing this anti-selection is undetermined by this
batch alone. Two candidate explanations (regime-mismatch vs
pattern-overfit) would make different forward predictions and require
multi-regime evaluation to distinguish. The mechanism question is
discussed in §9 as a load-bearing input to PHASE2C_7+ scoping.

**Bounded conclusion.** The corrected WF gate, as currently calibrated
(`wf_test_period_sharpe > 0.5`), did not enrich for 2022 holdout
survival in this batch. Within volume_divergence and momentum themes
specifically, the gate's selection process anti-selected against
2022-robust candidates. This is a finding about the corrected WF
metric's selection power for one regime in one batch; the bounds of
this claim are addressed in §6.

## 6. What this finding does NOT establish

§5 establishes a within-batch finding: the corrected WF gate did
not enrich for, and empirically anti-selected against, 2022-robust
candidates within batch b6fcbf86. §6 enumerates the bounds of that
finding — what the data does and does not allow a reader to
conclude. The bounds are split into three categories: data-scope
(what the batch covers and does not cover), interpretation-scope
(what the metric finding does and does not imply about adjacent
project work), and mechanism-scope (what the finding does and does
not say about why the anti-selection occurs).

**Data-scope bounds.**

This finding describes one batch (`b6fcbf86-4d57-4d1f-ae41-1778296b1ae9`),
one holdout regime (calendar year 2022), and one gate calibration
(`wf_test_period_sharpe > 0.5` for primary; the 4-criterion regime
holdout AND-gate from `config/environments.yaml` for survival). The
finding does not extend to:

- *Other batches from the same proposer.* A second batch sampling
  the same prompt-themed candidate space could produce a different
  primary/audit-only pass-rate relationship purely from sampling
  variance; the within-batch n=44 primary universe is small.

- *Other holdout regimes.* The 2022 holdout window contains a
  specific market shape (sustained directional bear, deep drawdowns,
  limited mean-reversion). A holdout sampled from 2024 (per the
  `v2` validation split), 2025 (test split), or any other regime
  could produce a different anti-selection profile. The within-batch
  finding establishes anti-selection against *this* regime, not
  against regimes in general.

- *Other gate calibrations.* The corrected WF gate threshold of
  0.5 was inherited from the Phase 2C Phase 1 binary criterion. A
  different threshold (0.0, 1.0) or a multi-criterion WF selection
  rule would partition the 198 candidates differently and could
  produce a different primary/audit-only relationship. The
  within-batch finding describes the threshold that was actually
  applied, not a property of any threshold the gate could use.

**Interpretation-scope bounds.**

This finding describes the corrected WF metric's selection power
for one regime in one batch. It does not imply that:

- *The corrected engine work was wasted or wrong.* The engine fix
  (commit `eb1c87f`, lineage `wf-corrected-v1`) corrected a
  semantic bug in walk-forward test-period metric computation. The
  bug fix is necessary and the metric values produced post-fix are
  the accurate measurements of what the metric is defined to
  measure. §5's finding is about what the (correctly-measured)
  metric *predicts* — specifically, that it does not predict 2022
  regime survival within this batch. A correctly-computed metric
  can fail to predict a property; that does not retroactively make
  the metric incorrect.

- *Walk-forward methodology is broken.* Walk-forward validation as
  a methodology comprises many design choices: window sizing, train
  vs test split semantics, metric aggregation, and the binary
  criterion applied to outputs. §5's finding speaks to one of these
  layers (the binary criterion `wf_test_period_sharpe > 0.5`
  applied to one set of WF outputs). Other design choices within
  walk-forward methodology — different window structures, different
  aggregation rules, different criteria — are not addressed by this
  batch. Generalizing from "this binary criterion underperformed
  on this batch's regime holdout" to "walk-forward methodology is
  broken" is an unwarranted extension.

- *Phase 2C generated no actionable strategies.* The closeout
  describes the corrected WF gate's failure to enrich for 2022
  robustness; it does not describe whether any Phase 2C candidate
  has alpha against any other regime. Specific candidates flagged
  in §7 (the 13 holdout-survivors) are 2022-survivors per the
  4-criterion gate but have not been evaluated against validation
  (2024) or test (2025) splits, against forward live data, or
  against any deployment-readiness criterion. No deployment claim,
  paper-trading claim, or "this strategy works" claim is made or
  implied.

- *Future regime holdouts will show similar patterns.* The within-batch
  anti-selection is empirically observed for 2022; whether it
  generalizes to other regimes is precisely the open question that
  PHASE2C_7+ scoping decisions need to consider (§9). The finding
  does not predict the outcome of a 2024 or 2025 holdout — it
  describes 2022 specifically.

**Mechanism-scope bounds.**

§5 surfaces the mechanism question (regime-mismatch vs pattern-overfit)
without committing to either explanation. §6 makes explicit that the
finding leaves the mechanism undetermined:

- *The data does not distinguish regime-mismatch from pattern-overfit.*
  Both candidate explanations would produce the empirical pattern
  observed (within-batch anti-selection against 2022-robust
  candidates). Distinguishing them requires holdout evaluations
  against multiple regime types, which is out of scope for PHASE2C_6.
  A reader cannot infer from this batch which explanation is
  correct, or whether some third explanation not enumerated is the
  actual mechanism.

- *The AND-gate question is empirically underdetermined.* A natural
  follow-up question is whether candidates that pass both the WF
  gate AND the regime holdout outperform candidates that pass either
  gate alone. This batch contains exactly 1 candidate satisfying
  both gates (`bf83ffec`, the borderline primary survivor). With
  n=1, no comparative claim about the AND-gate's selection power
  can be made from this data. PHASE2C_7+ would need a substantially
  larger candidate population, or evaluations across multiple
  holdout regimes, to address the AND-gate question empirically.

- *No claim about WF metric replacement.* The finding does not
  imply what the WF gate's threshold or criteria *should* be, what
  alternative selection metrics *would* enrich for 2022 robustness,
  or whether any selection metric can do so. PHASE2C_7+ scoping
  decisions about whether to revisit the WF metric, AND-gate it
  with the regime holdout, or replace it with a different selection
  framework are outside the bounds of what this batch's data
  supports.

**Summary of bounds.**

Within: this batch (b6fcbf86), this regime (2022), this gate
(`wf > 0.5` plus the 4-criterion AND-gate). The finding is real
within these bounds and operationally significant for PHASE2C_7+
scoping (per §9). Outside these bounds, the finding does not
extend without additional empirical work.

## 7. Survivor enumeration

The 13 candidates that passed the 2022 regime holdout 4-criterion
gate are listed below, grouped by theme and ordered by 2022 holdout
Sharpe (descending) within each theme. The table includes both
primary-universe (`wf_test_period_sharpe > 0.5`) and audit-only
(`wf_test_period_sharpe <= 0.5`) survivors. Two themes from the
batch's 5-theme rotation produced zero survivors and do not appear
below: `mean_reversion` (0 of 39 candidates) and `volatility_regime`
(0 of 40 candidates). Their absence is treated in §8.

| hash | univ. | theme | name | wf_sh | hd_sh | dd | ret | trades |
|------|-------|-------|------|------:|------:|---:|----:|-------:|
| 7f296ee9 | audit | calendar_effect | weekend_volatility_compression_monday_breakout_125 | −0.898 | +0.722 | 0.134 | +0.119 | 24 |
| 1d6a587a | audit | calendar_effect | monday_weakness_friday_strength | −0.203 | +0.586 | 0.151 | +0.109 | 52 |
| 94b3d1fd | audit | calendar_effect | monday_morning_accumulation | −0.192 | +0.479 | 0.120 | +0.070 | 34 |
| c200a95d | audit | calendar_effect | weekday_momentum_calendar_150 | +0.196 | +0.355 | 0.151 | +0.062 | 126 |
| bf83ffec | **primary** | calendar_effect | monday_weakness_tuesday_rebound_130 | +1.138 | +0.014 | 0.234 | −0.030 | 22 |
| 9dc5c373 | audit | calendar_effect | weekend_effect_momentum_185 | +0.434 | −0.046 | 0.166 | −0.016 | 78 |
| 0845d1d7 | audit | volume_divergence | volume_surge_momentum_entry | −0.072 | +0.508 | 0.095 | +0.068 | 19 |
| ab7584d2 | audit | volume_divergence | volume_divergence_breakout_159 | −0.207 | +0.398 | 0.153 | +0.059 | 47 |
| f4977b3e | audit | volume_divergence | volume_spike_momentum_entry | −0.753 | +0.347 | 0.159 | +0.050 | 65 |
| b2ddd47c | audit | volume_divergence | volume_divergence_breakout_momentum | −1.576 | −0.485 | 0.203 | −0.088 | 29 |
| 18c2a5f7 | audit | momentum | ema_crossover_momentum_surge | −1.511 | +0.960 | 0.079 | +0.125 | 20 |
| 37c0661e | audit | momentum | macd_momentum_surge_166 | −2.193 | +0.070 | 0.146 | −0.006 | 65 |
| 61395958 | audit | momentum | macd_rsi_momentum_confirmation_156 | −1.905 | −0.167 | 0.218 | −0.083 | 85 |

**Column key.** `hash` = first 8 hex characters of `hypothesis_hash`
(full 16-char hashes are in the per-candidate JSON artifacts under
`data/phase2c_evaluation_gate/audit_v1/<hash>/holdout_summary.json`).
`univ.` = which population the candidate belongs to (primary vs
audit-only). `wf_sh` = `wf_test_period_sharpe` from the corrected
batch artifacts. `hd_sh`, `dd`, `ret`, `trades` = 2022 regime
holdout Sharpe ratio, maximum drawdown, total return, and total
trade count.

**Two readings of the table.**

The first reading is *by row*. A reader scanning row-by-row sees
specific candidates with specific names and metrics. Notable rows:
the strongest 2022 holdout Sharpe in the entire batch is
`18c2a5f7` (momentum, hd_sh = +0.960), which the corrected WF gate
rejected at wf_sh = −1.511. The borderline primary-universe
survivor `bf83ffec` is at position 5 of 6 within its theme group
when sorted by hd_sh — within calendar_effect, the WF gate
selected a survivor, but not the strongest 2022-holdout candidates
by holdout Sharpe.

The second reading is *by structure*. Three of the five batch
themes produced survivors (calendar_effect: 6; volume_divergence: 4;
momentum: 3). Two produced none (mean_reversion: 0; volatility_regime:
0). Within each theme, the 1 primary survivor (bf83ffec) places
in the middle of its theme's hd_sh distribution rather than the
top — the within-theme echo of §5's anti-selection finding.
By-theme interpretation of these patterns is in §8; this section
enumerates without re-stating.

**Forensic access.** Per-candidate full evaluation summaries
(including `gate_pass_per_criterion` breakdown, `passing_criteria`
thresholds, `lineage_check` confirmation, and full strategy
metadata) are at:

```
data/phase2c_evaluation_gate/audit_v1/<hypothesis_hash>/holdout_summary.json
```

Trade-level CSVs are *not* stored under the evaluation-gate
artifact directory. When a candidate produced trades, the
underlying backtest wrote a trade log under
`data/results/trades_<run_id>.csv`, where `<run_id>` is recorded
in that candidate's `holdout_summary.json` under the `run_id`
field. Candidates that produced zero trades have no corresponding
trade-CSV file.

## 8. By-theme interpretation

The 5-theme rotation that produced this batch's 198 candidates
shows distinct patterns under the 2022 regime holdout. This section
treats each theme separately because the failure mechanisms diverge
in ways that grouping would erase, then synthesizes the patterns
that the five-theme view contributes beyond §5's load-bearing
finding. All claims are bounded to this batch, against the 2022
regime holdout; nothing in this section establishes general theme
properties across other regimes or other batches.

**calendar_effect (6 survivors of 40, 15.0%; primary 1/7,
audit-only 5/33).** This is the only theme that produced a
primary-universe survivor and the theme with the most total
survivors. Survivor 2022 holdout Sharpes range from −0.046 to
+0.722. A plausible structural reason calendar_effect survives at
a higher rate than directional themes is that day-of-week patterns
(Monday weakness, weekend effects, weekday momentum patterns) are
by definition not coupled to bull/bear directionality — Mondays
remain Mondays in trending bear regimes, so the alpha thesis can
fire without depending on regime structure. The within-theme
observation noted in §7 also holds here: the primary-universe
survivor (`bf83ffec`, hd_sh=+0.014) sits at position 5 of 6 within
its theme group when sorted by holdout Sharpe. The four audit-only
calendar_effect candidates above it (7f296ee9, 1d6a587a, 94b3d1fd,
c200a95d) all have stronger 2022 holdout Sharpes than the only
primary survivor — the within-theme echo of §5's anti-selection
finding.

**mean_reversion (0 survivors of 39, 0.0%; primary 0/14,
audit-only 0/25).** Zero survivors across both populations.
Failure-mode signature: 67% of failed candidates exceeded the 25%
drawdown threshold, 69% had Sharpe below −0.5, 67% had returns
below −15%. The mean-reversion thesis (buy weakness expecting
reversion to mean) repeatedly engaged with 2022's directional
bear and accumulated losses each time the expected reversion
didn't materialize. This is an *active-loss* failure mode:
strategies fired, took directional exposure, and suffered as the
mean kept moving down underneath them. The bounded interpretation:
within this batch, mean-reversion candidates do not survive the
2022 regime; the mechanism is regime-thesis mismatch rather than
gate calibration. This finding does not establish that mean-
reversion themes fail in all bear regimes (a steadier or
choppier bear market might supply different reversion dynamics)
or that mean-reversion themes should be dropped from future
proposer batches.

**volatility_regime (0 survivors of 40, 0.0%; primary 0/8,
audit-only 0/32).** Zero survivors across both populations, but
with a structurally distinct failure-mode signature from
mean_reversion: 48% of failed candidates fired fewer than 5
trades, and 18 of 40 candidates fired zero trades during the
entire 2022 holdout window. This is a *non-engagement* failure
mode: many volatility-regime strategies did not recognize a
regime they were designed to trade and remained inactive.
Strategies that did fire showed lower-magnitude failures than
mean_reversion (drawdown-failure rate 52%, sharpe-failure rate
42%), but the dominant mechanism here is silence rather than
active loss. The bounded interpretation: within this batch,
volatility-regime candidates either did not engage with 2022's
specific volatility structure or, when they did, did not survive
it. This does not establish that volatility-regime themes are
categorically broken — a holdout containing the volatility
patterns these strategies were designed to detect could produce
very different results.

**momentum (3 survivors of 39, 7.7%; primary 0/3, audit-only
3/36).** Within-theme inversion observable: zero primary
survivors (out of only 3 primary-universe candidates), three
audit-only survivors. The within-theme inversion strength is
attenuated by the small primary-universe n; with only 3 primary
candidates in this theme, the 0/3 outcome is consistent with both
"the WF gate empirically selects away from the 2022-survivors"
and "the primary universe was too small to contain the 2022-
surviving momentum candidates by chance." The audit-only survivors
include the strongest 2022 holdout Sharpe in the entire batch
(`18c2a5f7`, hd_sh=+0.960, wf_sh=−1.511 — the candidate the
corrected WF gate ranked near-worst within momentum). The bounded
interpretation: the within-theme inversion direction is consistent
with §5, but the primary n=3 limits the strength of the within-
theme claim specifically.

**volume_divergence (4 survivors of 40, 10.0%; primary 0/12,
audit-only 4/28).** Within-theme inversion observable with
larger primary universe: zero primary survivors of 12,
four audit-only survivors of 28. Unlike momentum, the n=12
primary universe is large enough to support a within-theme
anti-selection claim with less small-sample caveat — the WF
gate selected 12 candidates from this theme and none survived,
while the rejected 28 produced four survivors. The bounded
interpretation: within volume_divergence specifically, the WF
gate's selection was anti-correlated with 2022 holdout survival
in this batch.

**Synthesis.** Three patterns emerge from the by-theme view that
add to §5's load-bearing finding:

The first pattern is the regime-coupling distinction. Themes whose
alpha thesis is coupled to specific market structure
(mean_reversion to non-trending or reverting markets;
volatility_regime to specific volatility patterns) failed
systematically against the 2022 regime — but with mechanistically
different failure modes (mean_reversion engaged-and-lost;
volatility_regime did-not-engage). Themes with regime-orthogonal
theses (calendar_effect's day-of-week patterns) survived at
higher rate because the alpha source was independent of the
hostile regime structure.

The second pattern is the within-theme echo of §5's anti-selection
finding. Within calendar_effect, momentum, and volume_divergence
specifically, the WF gate empirically selected away from the
2022-survivors in these themes (with momentum carrying a small-n
caveat). The cross-theme anti-selection from §5 is corroborated
by within-theme observations in three of the five themes.

The third pattern is the heterogeneity of failure mechanisms.
A reader who interpreted §5's headline as "WF candidates lose
money in 2022" would miss that the two themes with zero
survivors fail in qualitatively different ways. mean_reversion
candidates accumulate active losses; volatility_regime
candidates often don't trade at all. Future evaluations
distinguishing "this theme's alpha thesis is regime-coupled" from
"this theme's gate calibration empirically selects away from
holdout survivors" need to look at failure-mode signatures, not
just pass rates.

These three patterns are descriptive of this batch against this
regime. Whether they generalize is an open empirical question
that PHASE2C_7+ scoping will need to address (§9).

## 9. Implications for PHASE2C_7+ scoping

This section enumerates open questions this batch raises and
decisions PHASE2C_7+ scoping will need to consider. It does not
make recommendations or pre-commit decisions; the methodology
discipline established in earlier closeouts and codified in
`docs/discipline/METHODOLOGY_NOTES.md` §3 (regime-aware
calibration bands) holds here: thresholds and operational
choices should not be pre-committed without empirical basis,
and one batch against one regime is not a sufficient empirical
basis for methodology-level decisions.

**Open questions this batch raises but does not answer.**

The first question is whether the corrected WF gate's anti-
selection generalizes beyond this batch and this regime. §5
establishes within-batch anti-selection against the 2022 holdout;
§5's mechanism-pointer paragraph names two candidate explanations
(regime-mismatch vs pattern-overfit) that would make different
forward predictions. Distinguishing them requires evaluation
against multiple holdout regimes — the 2024 validation split,
the 2025 test split (handled with touched-once discipline per
`config/environments.yaml`), or additional historical regimes
sampled deliberately to test specific mechanism predictions. With
data from one regime only, the question is empirically
underdetermined.

The second question is whether AND-gating (WF > 0.5 AND
holdout_passed) outperforms either gate alone. The natural
follow-up question to §5's anti-selection finding is whether
combining gates produces better selection than either gate
individually. This batch contains exactly one candidate
satisfying both gates (`bf83ffec`, the borderline primary
survivor); the n=1 population is too small to support any
comparative claim about AND-gate selection power. Two distinct
evidence paths could address the AND-gate question. A larger
candidate population evaluated against the same regime would test
whether AND-gate selection produces a meaningful dual-pass
population. The same candidates evaluated against multiple
regimes would test whether primary survivors generalize across
regimes or whether anti-selection persists. Either evidence path,
or both, could be appropriate depending on PHASE2C_7+ scoping
priorities.

The third question is whether the 4-criterion gate's trade-count
threshold (`total_trades >= 5`) is appropriately calibrated. §3
identifies four candidates that exhibited a distinctive failure
profile: positive 2022 holdout Sharpe, in-bound drawdown and
return, but firing fewer than 5 trades. These strategies
generated profitable signals when they fired but fired too
infrequently to satisfy the n=5 minimum. Whether such candidates
warrant separate consideration (e.g., a longer holdout window
that supplies more signal opportunities, or a calibration that
distinguishes "infrequent and profitable" from "frequent and
profitable") is a question the trade-count threshold raises but
does not resolve. Tightening or relaxing the threshold without
multi-regime evidence about how strategies in each cohort
generalize would be threshold-tuning without empirical basis.

The fourth question is what the 12 audit-only survivors
represent. These candidates passed the 2022 regime holdout
despite being rejected by the corrected WF gate. They are not
strategy recommendations — passing one regime holdout is not
sufficient evidence for deployment readiness, and these
candidates have not been evaluated against validation, test, or
forward live data. They are diagnostic material: empirical
evidence about what the corrected WF metric and the 2022 regime
holdout each select for, and how those selection criteria
diverge. Treating them as candidates for further study would
require a separate pre-registered question, not post-hoc
promotion because they survived 2022. Whether to investigate any
of these candidates further (e.g., evaluating them against the
2024 validation split to test the regime-mismatch vs
pattern-overfit mechanism hypotheses) is a PHASE2C_7+ scoping
decision that should be informed by what specific question that
investigation would answer.

**Decisions PHASE2C_7+ scoping will need to consider.**

The first decision is whether to invest in DSR (Deflated Sharpe
Ratio) infrastructure given the current primary survivor
population (n=1). DSR's deflation logic compares observed Sharpe
to a null distribution accounting for multiple-testing exposure;
with one survivor, the empirical population for deflation is too
small to support a meaningful batch-level DSR comparison. This is
a methodological observation, not a claim that DSR is misguided
in general. The question is whether this batch's specific output
supports the DSR analysis layer that earlier project planning
anticipated, or whether DSR investment should be deferred until a
population large enough to deflate meaningfully exists.

The second decision is whether to revisit the corrected WF gate's
binary criterion (`wf_test_period_sharpe > 0.5`) or supplement it
with alternative selection signals. §5 establishes that within
this batch, the corrected WF gate did not enrich for 2022 holdout
survival. Whether this finding warrants revisiting the binary
criterion depends on questions this batch does not answer (whether
the anti-selection generalizes; whether other selection metrics
would do better; whether the metric is meaningful for properties
other than 2022 robustness). The decision to revisit, supplement,
or maintain the current gate calibration is appropriately a
PHASE2C_7+ scoping decision after additional empirical evidence,
not a decision this closeout makes.

The third decision is whether to broaden holdout evaluation to
multiple regimes before drawing methodology-level conclusions.
This batch evaluated against one regime (2022). Either of the two
mechanism candidates from §5 (regime-mismatch, pattern-overfit)
would benefit from multi-regime evidence to distinguish, and
methodology-level claims about WF gate selection power that
extend beyond this batch require broader empirical sampling. The
operational form of this decision (which regimes, in what
sequence, against which candidate populations) is itself a
PHASE2C_7+ scoping question that depends on what specific
mechanism claim or selection-power claim PHASE2C_7+ aims to
establish.

**Explicit non-decisions.** This closeout does not recommend:
that the WF gate be replaced; that DSR infrastructure investment
be cancelled; that mean_reversion or volatility_regime themes be
removed from future proposer batches; that any specific candidate
be advanced to validation, test, paper-trading, or live work; or
that the 4-criterion regime holdout gate calibration be adjusted.
Each of these is a decision the data could potentially inform but
that this batch alone does not establish. PHASE2C_7+ scoping is
the appropriate venue for these decisions, with the discipline
that decisions backed by one batch against one regime should be
made cautiously and reversibly.

## 10. Methodology-discipline observation

Two project-discipline observations from this work cycle warrant
brief mention; full codification is deferred to a follow-up update
of `docs/discipline/METHODOLOGY_NOTES.md` rather than carried in this
closeout.

The first observation is the scaling-step pattern. The PHASE2C_6
arc executed three runs (smoke 4-candidate; primary 44-candidate;
audit 198-candidate), each adding necessary information that earlier
steps could not provide. The smoke run verified plumbing — script
correctness, lineage stamping, failure handling — but produced no
universe-level claim. The primary run established the
primary-universe result (1 of 44 winners passed) but did not yet
enable the comparative claim §5 ultimately carries. The audit run
produced the comparative finding (audit-only > primary pass rate)
which is the closeout's load-bearing result. Each scaling step's
data was necessary; earlier-step data alone was insufficient.
Treating smoke results or primary-only results as decision-quality
evidence would have over-weighted the data and produced
under-supported conclusions. The discipline lesson: scale empirical
evaluations deliberately, and do not draw load-bearing conclusions
from intermediate steps without the data the later steps will
provide.

The second observation is the cumulative value of the empirical-
verification discipline (METHODOLOGY_NOTES.md §1) during closeout
drafting. Multiple specific defects were caught at draft time rather
than at cold-read time, including the near-miss cluster size (3 vs 4
candidates), the survivor's holdout Sharpe precision (rounding vs
full-precision), the trade-CSV artifact location (per-candidate
directory vs `data/results/`), and the by-theme failure-mode
mechanism distinction (mean_reversion engaged-and-lost vs
volatility_regime did-not-engage). Each defect would have shipped if
the section's prose had been written from plausible-reasoning rather
than from CSV-query-against-canonical-artifacts. The discipline
pattern is not specific to this closeout — it has caught defects
throughout the corrected-engine arc and the Phase 2C work that
preceded it — but the cumulative pattern this cycle adds confirming
evidence that empirical query before prose is a load-bearing
discipline for closeout integrity.

## 11. References and reproducibility

**Run commands.** All three runs are reproducible from the
canonical `b6fcbf86` source batch using
`scripts/run_phase2c_evaluation_gate.py`:

```bash
# PHASE2C_6.3 smoke
python scripts/run_phase2c_evaluation_gate.py \
  --source-batch-id b6fcbf86-4d57-4d1f-ae41-1778296b1ae9 \
  --candidate-hashes 0bf34de1,812216d4,56def67e,9436a54b \
  --run-id smoke_v1

# PHASE2C_6.4 primary universe
python scripts/run_phase2c_evaluation_gate.py \
  --source-batch-id b6fcbf86-4d57-4d1f-ae41-1778296b1ae9 \
  --universe primary --run-id primary_v1

# PHASE2C_6.5 audit universe
python scripts/run_phase2c_evaluation_gate.py \
  --source-batch-id b6fcbf86-4d57-4d1f-ae41-1778296b1ae9 \
  --universe audit --run-id audit_v1
```

**Reproducibility queries.** The closeout's headline numbers can
be independently verified from the canonical CSV artifacts:

```python
import csv

# Headline: primary universe pass rate (1/44 = 2.27%)
with open("data/phase2c_evaluation_gate/primary_v1/"
          "holdout_results.csv") as f:
    rows = list(csv.DictReader(f))
passed = sum(1 for r in rows if r["holdout_passed"] == "1")
total = len(rows)
print(f"primary: {passed}/{total} = {passed/total*100:.2f}%")
# expected: primary: 1/44 = 2.27%

# Headline: audit universe pass rate (13/198 = 6.57%)
with open("data/phase2c_evaluation_gate/audit_v1/"
          "holdout_results.csv") as f:
    audit_rows = list(csv.DictReader(f))
audit_passed = sum(1 for r in audit_rows if r["holdout_passed"] == "1")
print(f"audit: {audit_passed}/{len(audit_rows)} = "
      f"{audit_passed/len(audit_rows)*100:.2f}%")
# expected: audit: 13/198 = 6.57%

# §5 comparative: audit-only > primary
primary_subset = [r for r in audit_rows
                  if float(r["wf_test_period_sharpe"]) > 0.5]
audit_only = [r for r in audit_rows
              if float(r["wf_test_period_sharpe"]) <= 0.5]
ps_pass = sum(1 for r in primary_subset if r["holdout_passed"] == "1")
ao_pass = sum(1 for r in audit_only if r["holdout_passed"] == "1")
print(f"primary subset:    {ps_pass}/{len(primary_subset)} = "
      f"{ps_pass/len(primary_subset)*100:.2f}%")
print(f"audit-only:        {ao_pass}/{len(audit_only)} = "
      f"{ao_pass/len(audit_only)*100:.2f}%")
# expected: primary subset: 1/44 = 2.27%
#           audit-only: 12/154 = 7.79%

# §8 by-theme breakdown
from collections import defaultdict
themes = defaultdict(lambda: [0, 0])
for r in audit_rows:
    themes[r["theme"]][0] += 1
    if r["holdout_passed"] == "1":
        themes[r["theme"]][1] += 1
for t, (total, passed) in sorted(themes.items()):
    print(f"{t:<22} {passed}/{total} = {passed/total*100:.1f}%")
# expected:
#   calendar_effect        6/40 = 15.0%
#   mean_reversion         0/39 = 0.0%
#   momentum               3/39 = 7.7%
#   volatility_regime      0/40 = 0.0%
#   volume_divergence      4/40 = 10.0%
```

**Lineage round-trip.** Every artifact in
`data/phase2c_evaluation_gate/{smoke,primary,audit}_v1/` validates
under the consumer-side guard:

```python
import json
from pathlib import Path
from backtest.wf_lineage import check_evaluation_semantics_or_raise

base = Path("data/phase2c_evaluation_gate")
for run in ["smoke_v1", "primary_v1", "audit_v1"]:
    run_dir = base / run
    paths = [run_dir / "holdout_summary.json"] + sorted(
        run_dir.glob("*/holdout_summary.json"))
    for p in paths:
        d = json.load(open(p))
        check_evaluation_semantics_or_raise(d, artifact_path=str(p))
print("all artifacts validate")
```

**Cross-references.**

- Plan: `docs/phase2c/PHASE2C_6_EVALUATION_GATE_PLAN.md` (PHASE2C_6
  scoping doc)
- Lineage discipline: `docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md`
  (Section RS hard prohibition; producer + consumer attestation)
- Corrected engine arc: `docs/closeout/CORRECTED_WF_ENGINE_SIGNOFF.md`
  (engine fix at commit `eb1c87f`, lineage tag `wf-corrected-v1`)
- Phase 2C Phase 1 results: `docs/closeout/PHASE2C_5_PHASE1_RESULTS.md`
  + erratum `PHASE2C_5_PHASE1_RESULTS_ERRATUM.md` (corrected
  binary-criterion count: 44/198, source for primary universe)
- Methodology principles applied:
  `docs/discipline/METHODOLOGY_NOTES.md` §1, §2, §3
- Consumer guard implementation: `backtest/wf_lineage.py`
  (`check_evaluation_semantics_or_raise`)
- Producer script: `scripts/run_phase2c_evaluation_gate.py`
- Tests: `tests/test_phase2c_evaluation_gate_runner.py`,
  `tests/test_wf_lineage_guard.py`

**Commit chain (this branch, `claude/phase2c-evaluation-gate`):**

- `e4a2591` PHASE2C_6.0 scoping doc
- `81f8b73` PHASE2C_6.0 amendment (smoke convention pinning)
- `e29b599` PHASE2C_6.1 consumer guard helper +
  `check_evaluation_semantics_or_raise`
- `72c1270` PHASE2C_6.2 producer script + tests
- `ca096ef` PHASE2C_6.3 smoke artifacts
- `d6f481a` PHASE2C_6.4 primary artifacts
- `e6cecb9` PHASE2C_6.5 audit artifacts
- This document: PHASE2C_6.6 closeout document.
