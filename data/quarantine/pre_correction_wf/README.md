# Pre-Correction WF Artifact Quarantine

These artifacts were produced by `scripts/run_phase2c_batch_walkforward.py`
under the pre-correction WF engine (commit `0531741` and ancestors). They
are kept for historical reproducibility of the original Phase 2C Phase 1
closeout but MUST NOT be consumed by any downstream decision (DSR, PBO,
CPCV, MDS, strategy shortlist, research-direction, erratum sign-off).

The corrected WF engine commit is `eb1c87f` (`fix(engine): WF gated wrapper
implements Q2 (iii)`). Corrected re-runs live at
`data/phase2c_walkforward/<batch_id>_corrected/` and carry the metadata
field `wf_semantics: corrected_test_boundary_v1`.

See `docs/decisions/WF_TEST_BOUNDARY_SEMANTICS.md` Section RS for the
canonical hard prohibition.
