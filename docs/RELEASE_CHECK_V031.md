# v0.3.1 release check

Date: 2026-11-22 (Asia/Shanghai)

## Release decision

The Recursive Freedom Audit rule-quality update is ready for the controlled
commercial pilot. It adds a dedicated product entry at `/recursive-freedom` and
replaces broad word matches with compound evidence rules.

## Verification

| Check | Result |
|---|---|
| Python test suite | 74 passed |
| Ruff check | Passed with Windows mount `EXE002` ignored |
| Ruff format | 33 files already formatted |
| TypeScript | Passed |
| Wrangler dry run | Passed |
| Inline browser scripts | Both parsed |
| Local 0.3.1 container health | Passed |
| Complete synthetic policy | 10 present, 0 partial, 0 missing |
| Negative-language policy | Expected governance checks remained missing |
| Report version | 0.3.1 |
| Methodology version | `RFP-AI-policy-structure-v0.2` |

## Development benchmark

Five public documents and 50 check-level decisions were reviewed:

| Metric | Result |
|---|---:|
| Documents | 5 |
| Check-level decisions | 50 |
| Exact status matches | 50 |
| Expected present or partial checks | 19 |
| Detected present or partial checks | 19 |
| Recorded false positives | 0 |
| Recorded false negatives | 0 |

The benchmark is a Codex-assisted written adjudication. It is not independent
validation and is not a fully held-out test because rule refinements followed
the first review.

## Production acceptance

The existing end-to-end production script passed:

- invalid API key rejection;
- fresh quota;
- AI policy mode with ten checks;
- ESG commitment mode;
- cross-tenant isolation;
- one quota unit per successful mode;
- 101-page PDF rejection;
- quota refund;
- report deletion;
- deletion does not restore quota.

The temporary production organizations and keys were removed after the test.

## Remaining gates

- Expand to at least ten documents and 100 check-level decisions.
- Add a true held-out sample that is not used for rule tuning.
- Obtain at least one independent AI-governance or policy review.
- Test representative Chinese-language policies.
- Add version-to-version comparison before launching a separate paid product.
- Keep the formal Codex plugin package paused until the separate product scope
  and pricing are approved.
