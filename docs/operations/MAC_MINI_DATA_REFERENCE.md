# Off-repo cold-storage data reference

**Purpose**: operational reference for recovering `raw_payloads/` data that has been pruned from this development repo but is preserved on a separate cold-storage host (the original production machine where Phase 2C / Phase 4 cohort generation ran).

**When to consult this doc**: if any cycle reports `INDETERMINATE-DSL-UNAVAILABLE`, `0/N raw_payloads accessible`, "raw_payloads gap", or otherwise references missing batch directories under `raw_payloads/`, **check the cold-storage host before declaring permanent data loss**. The historical pattern has been: data was generated on the cold-storage host, the development machine has only the subset that was ever rsync'd, the cold-storage host retains the full superset.

## Connection (via SSH alias)

This doc references the cold-storage host symbolically as `mac-mini-cold-storage`. The real hostname / user / identity file live **only in your local `~/.ssh/config`** (never committed). To use the recovery commands in this doc, ensure your `~/.ssh/config` includes:

```
Host mac-mini-cold-storage
    HostName <LAN IP or hostname of cold-storage machine>
    User <username on cold-storage machine>
    IdentityFile ~/.ssh/id_ed25519
```

with `chmod 600 ~/.ssh/config`. The cold-storage host must have your public key (`~/.ssh/id_ed25519.pub`) in its `~/.ssh/authorized_keys`.

If SSH fails with `Permission denied (publickey,...)`, ensure the host is online (cold-storage is typically not powered 24/7) and the public key is registered. Ask the project owner if you do not have these values locally; they are intentionally not in the committed doc.

## Cold-storage host state (as of 2026-05-26)

- Git HEAD on cold-storage is **hundreds of commits behind** this development machine. The cold-storage host's value is **raw data preservation**, not code preservation; code is fully maintained in this repo's git history + on GitHub.
- Do **not** sync the cold-storage host's code (e.g. `git pull` on that machine) unless explicitly authorized; the older HEAD is a historical reference for "what code state produced the original artifacts."

## Inventory snapshot 2026-05-26

On the cold-storage host, `~/btc-alpha-pipeline/raw_payloads/` contains:

```
raw_payloads/
├── batch_355a8f9f-2a1f-435d-a1a8-c365b92e185b/   ← PHASE2C_15 cohort_a source #1 (~3.2M; 200 attempt responses)
├── batch_4f894318-eb69-48b5-95ef-e22abe3ecdd1/   ← PHASE2C_15 cohort_a source #2 (~3.3M; 200 attempt responses)
├── batch_5cf76668-47d1-48d7-bd90-db06d31982ed/   ← Also present on development machine
├── batch_71d42a07-d88f-431a-a653-601010cf1921/   ← PHASE2C_15 cohort_a source #3 (~3.3M; 200 attempt responses)
├── batch_91ad68ed-6470-45a7-8735-171c39ff25c3/   ← PHASE2C_15 cohort_a source #4 (~3.2M; 200 attempt responses)
├── batch_a12c2a65-4314-4dde-be6e-968a0c70ee6e/   ← PHASE2C_15 cohort_a source #5 (~3.2M; 200 attempt responses)
└── batch_phase2c_15_main_fire_combined/          ← Synthetic dir: 993 attempt_NNNN symlinks → sub-batch local positions
                                                     + 5 source_stage2d_summary_*.json symlinks
```

The combined dir is the **synthetic union** of the 5 cohort_a source batches with attempt files numbered globally 1-993. Each `attempt_NNNN_response.txt` is a relative symlink pointing into one of the 5 sub-batch directories. The producer at `scripts/run_phase2c_evaluation_gate.py:331` (`_load_dsl_from_response(source_batch_id="phase2c_15_main_fire_combined", position=N)`) reads via this combined dir.

## Recovery command template (verified 2026-05-26)

Use the macOS-default rsync (2.6.9) compatible flags. All real values come from `~/.ssh/config` via the alias:

```bash
# Single batch:
rsync -a -v --progress \
  mac-mini-cold-storage:btc-alpha-pipeline/raw_payloads/batch_<UUID> \
  ./raw_payloads/
```

For the cohort_a 6-dir bundle (the package recovered 2026-05-26):

```bash
rsync -a -v --progress \
  mac-mini-cold-storage:btc-alpha-pipeline/raw_payloads/batch_355a8f9f-2a1f-435d-a1a8-c365b92e185b \
  mac-mini-cold-storage:btc-alpha-pipeline/raw_payloads/batch_4f894318-eb69-48b5-95ef-e22abe3ecdd1 \
  mac-mini-cold-storage:btc-alpha-pipeline/raw_payloads/batch_71d42a07-d88f-431a-a653-601010cf1921 \
  mac-mini-cold-storage:btc-alpha-pipeline/raw_payloads/batch_91ad68ed-6470-45a7-8735-171c39ff25c3 \
  mac-mini-cold-storage:btc-alpha-pipeline/raw_payloads/batch_a12c2a65-4314-4dde-be6e-968a0c70ee6e \
  mac-mini-cold-storage:btc-alpha-pipeline/raw_payloads/batch_phase2c_15_main_fire_combined \
  ./raw_payloads/
```

**Post-rsync verification**:

```bash
# 1. File count of combined dir (should be 993):
ls raw_payloads/batch_phase2c_15_main_fire_combined/attempt_*_response.txt | wc -l

# 2. Symlink resolution (should be -> ../batch_91ad68ed-.../attempt_0080_response.txt):
ls -la raw_payloads/batch_phase2c_15_main_fire_combined/attempt_0873_response.txt

# 3. End-to-end DSL load (should succeed + print candidate name):
python3 -c "from scripts.run_phase2c_evaluation_gate import _load_dsl_from_response; \
  dsl = _load_dsl_from_response('phase2c_15_main_fire_combined', 873); print('DSL.name:', dsl.name)"
```

## Historical INDETERMINATE classifications that this data resolves

The 5 cohort_a source batches (`355a8f9f` / `4f894318` / `71d42a07` / `91ad68ed` / `a12c2a65`) are the SINGLE common driver of `0/5 raw_payloads accessible` declarations in the following SEAL artifacts:

| SEAL artifact | Section | INDETERMINATE classification | Recoverable via cold-storage? |
|---|---|---|---|
| `R2_1_STRATUM_B_DSL_AUDIT_NOTE.md` | §5 | 0/4 target D3-hash matches in compiled_strategies + raw_payloads | ✓ Yes (re-run D3-hash matching against recovered responses) |
| `R2_3_THEME_TAG_PROVENANCE_NOTE.md` | sub-claims | theme_override + post-rotation-filtering claims not verifiable | ✓ Yes |
| `R5_1_PHASE_B_CANDIDATE_SUBSET_COMMITMENT_NOTE.md` | §3 dim (d) | 37 candidates carry `INDETERMINATE-DSL-UNAVAILABLE` | ✓ Yes (re-verify dim (d) per candidate against recovered DSLs) |
| `R5_2_PHASE_B_SELECTION_INFLATION_HANDLING_NOTE.md` | §3.X | Carry-forward from R5.1 | ✓ Yes |
| `R6_1_TIER_6_PROMOTION_CLASS_NOTE.md` | §8 (4-of-7 INDETERMINATE) | Driven by 2 distinct gaps: (a) DSL unavailability (=0/5 raw_payloads) AND (b) per-bar return series + γ3/γ4 not preserved at engine→writer boundary | ⚠️ Partial. (a) recoverable via cold-storage. (b) still requires B-C-narrow engine re-run (this is the cycle currently in design) |
| `B_C_EXTENDED_SCOPE_B_NOTE.md` | (driver for R6.1) | Engine→writer artifact-preservation gap | ✗ No — this is the engine-layer infrastructure gap, not the raw_payloads gap; addressed by T1.x SEAL work (already done) + B-C-narrow consumer wiring (current cycle) |

**Discipline note (sealed-content invariance):** Per Architecture B precedent (R6.1 §2.2 narrow patch errata) + R3.1a §12 + R2.3 β3 hybrid, none of the above SEAL artifacts should be modified in place. The INDETERMINATE classifications were correct at their SEAL register-event time. The new fact "DSL data recoverable via cold-storage 2026-05-26" is an empirical follow-up that may be referenced by future successor cycles via errata supplement, NOT by retroactively editing the sealed text.

## Cross-references

- `METHODOLOGY_NOTES.md` §34 — Data-accessibility pre-verification standing rule; this doc is the operational follow-up registry
- `METHODOLOGY_NOTES.md` §35.9 — Data-preservation as pre-commit audit criterion at artifact-design boundary; this doc reaffirms §35.9 by registering off-repo cold-storage location
- `docs/phase5/R6_1_TIER_6_PROMOTION_CLASS_NOTE.md` §10 — B-C-narrow successor cycle named (current cycle in design)
- `docs/phase5/B_C_EXTENDED_SCOPE_B_NOTE.md` §1 — Scope-B engine-layer infrastructure (T1.1-T1.6 SEAL)

## Security / opsec note

This doc is **public-repo-safe by construction**: it references the cold-storage host only via the SSH alias `mac-mini-cold-storage`, never via IP / username / absolute paths. Real connection values live in your local `~/.ssh/config` (gitignored by being outside the repo). Maintainers should preserve this abstraction when updating this doc — do not paste IPs, usernames, or full absolute paths into committed text.

## Maintenance

If raw_payloads inventory on the cold-storage host changes (new batch produced, batch pruned, etc.), update the "Inventory snapshot" section above with a new dated entry. Append-only; preserve prior snapshots for audit history.

If the cold-storage host is ever decommissioned or replaced, **migrate `~/btc-alpha-pipeline/raw_payloads/` off the host to a permanent backup location BEFORE decommissioning** — this is the only known copy of the cohort_a source batches.
