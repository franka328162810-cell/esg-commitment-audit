# AI Alignment Revisability Policy

Effective date: 1 December 2026.

## Scope and hierarchy

This policy governs all production AI systems and AI agents operated by the
organisation. The alignment target is the AI Constitution v2.3.0.

Redline principles have precedence over procedures and operational guidance.
Conflicts of principles are escalated to the Independent AI Ethics Panel for
adjudication.

## Authority

The policy owner is the Chief AI Officer. The revision procedure requires
approval by the AI Governance Board after a documented impact assessment.

A 60-day public consultation is held before a material change to a redline or
core principle. The consultation record identifies participants, submissions,
and unresolved dissent.

## Revision

The alignment target is reviewed annually and after every serious incident. A
material change or serious incident triggers a revision by the responsible
owner.

High-impact changes use a staged rollout and a controlled sandbox. Each stage has
documented success criteria, stop conditions, and a comparison with the prior
state.

## Version and history

Every release has a unique version number using semantic versioning. A change
log records the reason, proposer, approver, affected clauses, and evidence
considered for each revision.

Previous versions remain available in a public archive. A rollback creates a new
forward version and does not delete the version history.

## Reversibility

Rollback when a warning threshold is exceeded, a redline is breached, or a
serious incident occurs. Rollback is approved by the Incident Commander and
reviewed by the AI Governance Board after the event.

A rollback drill is conducted every six months. The rollback exercise record
includes scope, result, defects found, corrective actions, and evidence that
software, data, model, and external effects were handled.

Fundamental rights and redline commitments require a supermajority to amend and
cannot be rolled back without an independent review.

## Affected people

Affected users receive 30 days advance notice before a material change takes
effect. A plain-language summary explains the reason for the change, impact
assessment, evidence, and unresolved uncertainty.

Users may appeal and request human review. They may opt out of optional
processing and exit the service without retaliation.

## Monitoring and records

Monitoring metrics and warning thresholds cover drift, incidents, complaints,
and revision deadlines. Exceptions are escalated to the accountable owner.

Audit logs are append-only and tamper-evident. Evidence is retained for seven
years and preserved under a legal hold when a dispute is notified.

## Oversight and technical controls

Independent review is conducted by an external auditor with access to the
Governance Board. A cooling-off period, conflict-of-interest check, and
anti-retaliation rule apply to revision and rollback decisions.

The policy acknowledges deep uncertainty: when confidence thresholds are not
met, the target is reconsidered rather than treated as permanently correct.

A release gate requires a pre-deployment evaluation, named approval, and a stop
condition. A kill switch and emergency shutdown procedure are tested; an
interruption test records response time, state preservation, and override
authority.
