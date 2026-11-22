# Recursive Freedom Audit for AI

## Product scope

Recursive Freedom Audit for AI reviews whether an AI policy, model card, or
governance document supplies the written mechanisms needed to revise rules
without locking affected people into an unaccountable arrangement.

The product checks written structure. It does not test an individual's
personality, political views, employability, creditworthiness, insurability,
education eligibility, immigration status, or legal culpability. It does not
certify legal compliance or prove how an AI system behaves.

Product page:

```text
https://esg-commitment-audit-api.franka328162810.workers.dev/recursive-freedom
```

Public sample report:

```text
https://esg-commitment-audit-api.franka328162810.workers.dev/recursive-freedom/sample
```

## Ten checks

| Check | Question |
|---|---|
| Scope and accountable owner | What does the document govern, when is it effective, and who owns it? |
| Review cadence | Is there a scheduled opportunity to reconsider the rules? |
| Revision authority and process | Who may propose and approve changes, and through what procedure? |
| Version history and change log | Can readers trace what changed and recover prior versions? |
| Advance notice | Are affected people told before material changes take effect? |
| Appeal and human review | Can a person challenge a decision or request human review? |
| Refusal, opt-out, and exit | Can affected people decline or leave? |
| Monitoring, audit logs, and evidence | What evidence shows whether the controls operate? |
| Rollback, suspension, and deprecation | Can a failed policy or system change be withdrawn? |
| Independent oversight | Is any review conducted outside the operating team? |

## Status rules

`present` means the text contains the relevant structural control and source
evidence. `partial` means some supporting language is present but a material
element is absent. `missing` means the examined text did not support the check.

Missing evidence does not prove that the organization lacks an internal
practice. It means the public or reviewed document does not contain the relevant
commitment.

## v0.2 development benchmark

The v0.2 rules were tested against five public documents:

- OpenAI Usage Policies
- Anthropic Usage Policy
- Google Generative AI Prohibited Use Policy
- Anthropic Responsible Scaling Policy
- Google DeepMind's introduction to the Frontier Safety Framework

The benchmark contains 50 check-level decisions. The current rules matched the
written adjudication in 50 cases. Nineteen checks were expected to be either
present or partial; all 19 were detected, with zero recorded false positives
and zero recorded false negatives.

These figures are not independent validation. The review was performed by Codex
under written rules, the sample is small, and the rules were refined after
examining initial false positives. The benchmark is a development gate for
finding obvious lexical errors, not evidence that the product is scientifically
validated.

## Errors corrected in v0.2

- Generic references to consent no longer count as a refusal or exit route.
- General references to legal oversight no longer count as independent
  oversight.
- Suspending a user's access no longer counts as policy or system rollback.
- Human-in-the-loop review of a high-risk recommendation no longer counts as a
  policy-review cadence.
- A public updates page no longer counts as advance notice unless the text
  states that notice occurs before the change.
- General monitoring no longer counts as audit-log evidence.
- A scope statement alone no longer counts as a complete scope, owner, and
  effective-date check.

## Product family

Recursive Freedom Audit for AI is the policy-text audit. It does not absorb two
adjacent products:

- **AI Public Commitment & Revision Monitor** is a future data product that
  tracks public commitments and policy changes over time.
- **Organizational Revisability Audit** is a future professional service that
  tests actual governance, appeals, exit paths, and continuity.

`AI Commitment and Revision Monitor` is retired as a separate public product
name because it overlaps with both names above.

## Commercial status

The audit is currently included in the US$29/month Founding plan as a Beta
mode. It has no separate subscription and no formal Codex plugin package yet.
Before a separate paid launch, the product needs a larger benchmark, at least
one independent review, representative Chinese-language documents, and
version-to-version comparison testing.
