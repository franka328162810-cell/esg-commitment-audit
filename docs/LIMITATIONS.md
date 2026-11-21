# Limitations and use boundaries

## What the result means

The output is a structural review of a written commitment. It identifies
whether the text supplies information needed for observation, implementation,
and revision. It does not establish that the commitment is honest, achievable,
consistent with science, or legally compliant.

## What the tool cannot do

- It cannot verify emission data against external sources.
- It cannot infer an unwritten baseline, method, owner, or remedy.
- It cannot certify CSRD, SBTi, ISSB, GRI, TCFD, or any other framework.
- It cannot decide greenwashing.
- It cannot replace legal, audit, assurance, or investment due diligence.

## Technical limitations

- Scanned PDFs require OCR, which is excluded from v0.3.0.
- Complex tables and multi-column layouts may require manual review.
- Chinese and English rule coverage is broader than other languages.
- The rule engine is intentionally conservative and may miss paraphrases.
- The internal benchmark is not an independent validation dataset.
- The AI Policy Revision Audit is a Beta checklist of written controls. It does
  not establish that a control exists in practice, works as described, or meets
  any legal or safety standard.

## Privacy

The default CLI, local web server, and Codex local-audit tool process files on
the user's machine. Local mode has no telemetry and makes no outbound network
request as part of an audit.

The commercial API is an explicit opt-in path. It stores tenant metadata,
uploads the selected source document for processing, deletes the input after
the job, and retains the resulting evidence report until its configured
retention deadline. Operators must publish their own privacy, retention, and
data-processing terms before accepting customer documents.
