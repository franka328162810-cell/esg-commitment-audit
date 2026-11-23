const style = `
  :root { color-scheme: light; font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
  [hidden] { display: none !important; }
  body { margin: 0; color: #182126; background: #f4f7f5; }
  main { max-width: 860px; margin: 0 auto; padding: 48px 24px 80px; }
  article { background: #fff; border: 1px solid #dbe4df; border-radius: 18px; padding: 32px; }
  h1 { font-size: clamp(2rem, 5vw, 3.6rem); line-height: 1.05; margin: 0 0 16px; }
  h2 { margin-top: 34px; font-size: 1.3rem; }
  p, li { line-height: 1.75; }
  a { color: #08734f; }
  .eyebrow { text-transform: uppercase; letter-spacing: .12em; color: #08734f; font-weight: 700; }
  .notice { border-left: 4px solid #d69219; background: #fff8e8; padding: 14px 18px; }
  .muted { color: #5e6b66; }
  nav { display: flex; flex-wrap: wrap; gap: 18px; margin-top: 30px; }
  .actions { display: flex; flex-wrap: wrap; gap: 12px; margin: 26px 0; }
  .button { display: inline-block; padding: 12px 18px; border: 1px solid #08734f; border-radius: 9px; background: #08734f; color: #fff; font-weight: 700; text-decoration: none; cursor: pointer; }
  .button.secondary { background: #fff; color: #08734f; }
  .button.danger { border-color: #a33a2b; background: #a33a2b; }
  .button:disabled { cursor: not-allowed; opacity: .55; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin: 20px 0; }
  .card { border: 1px solid #dbe4df; border-radius: 12px; padding: 18px; background: #fbfdfc; }
  label { font-weight: 650; }
  input[type="password"], input[type="text"], select { box-sizing: border-box; width: 100%; padding: 12px; border: 1px solid #aab8b1; border-radius: 8px; background: #fff; font: inherit; }
  .field-row { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }
  .field-row input { flex: 1 1 320px; }
  .mode-card { display: block; border: 2px solid #dbe4df; border-radius: 12px; padding: 18px; background: #fff; cursor: pointer; }
  .mode-card .muted { display: block; margin-top: 6px; }
  .mode-card input { margin-right: 8px; }
  .mode-card:has(input:checked) { border-color: #08734f; background: #f0faf6; }
  .dropzone { border: 2px dashed #8aa49a; border-radius: 12px; padding: 28px 18px; text-align: center; background: #fbfdfc; cursor: pointer; }
  .dropzone.active { border-color: #08734f; background: #edf9f3; }
  .status { min-height: 1.5em; color: #31534a; }
  .error { border-left: 4px solid #a33a2b; background: #fff1ef; padding: 12px 16px; }
  .success { border-left: 4px solid #08734f; background: #edf9f3; padding: 12px 16px; }
  .report { margin-top: 30px; }
  .report-card { border: 1px solid #dbe4df; border-radius: 12px; padding: 18px; margin: 14px 0; background: #fff; }
  .evidence { border-left: 3px solid #9aa9a2; padding-left: 14px; color: #34443e; }
  .status-pill { display: inline-block; border-radius: 999px; padding: 3px 9px; font-size: .84rem; font-weight: 700; background: #edf1ef; }
  .status-present { background: #dff5ea; color: #075c41; }
  .status-partial { background: #fff1c9; color: #785600; }
  .status-missing { background: #ffe2dd; color: #8b2d20; }
  .status-documented { background: #dff5ea; color: #075c41; }
  .status-asserted { background: #fff1c9; color: #785600; }
  .status-absent { background: #edf1ef; color: #4e5d57; }
  .status-contradicted { background: #ffe2dd; color: #8b2d20; }
  .status-operationally_evidenced { background: #e4eefc; color: #174e80; }
  .status-independently_verified { background: #eee8fa; color: #4d3678; }
  .status-not_assessable { background: #edf1ef; color: #4e5d57; }
  .table-wrap { overflow-x: auto; margin: 20px 0; }
  .data-table { width: 100%; border-collapse: collapse; font-size: .94rem; }
  .data-table th, .data-table td { border-bottom: 1px solid #dbe4df; padding: 10px 12px; text-align: left; vertical-align: top; }
  .data-table th { background: #21384a; color: #fff; font-weight: 700; }
  .data-table tr:nth-child(even) td { background: #f6f9f8; }
  pre { white-space: pre-wrap; word-break: break-word; }
`;

function page(title: string, body: string, lang = "zh-CN"): string {
  return `<!doctype html>
<html lang="${lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${title}</title>
  <style>${style}</style>
</head>
<body>
  <main>${body}</main>
</body>
</html>`;
}

export const landingPage = page(
  "ESG Commitment Audit | Evidence workbench",
  `<article>
    <p class="eyebrow">ICS-TEC / ICS STUDIES</p>
    <h1>Audit the wording before you rely on the promise.</h1>
    <p>ESG Commitment Audit turns long sustainability and climate reports into traceable commitment evidence. AI Alignment Revisability Audit applies the same evidence discipline to AI rules, constitutions, model cards, and revision paths.</p>
    <div class="actions">
      <a class="button" href="https://icsstudies.gumroad.com/l/esg-commitment-audit" rel="noopener">Subscribe to ESG Audit — US$29/month</a>
      <a class="button" href="https://icsstudies.gumroad.com/l/ai-alignment-revisability-audit" rel="noopener">Subscribe to AI Audit — US$99/month</a>
      <a class="button secondary" href="/workspace">Open the workbench</a>
    </div>
    <p class="notice"><strong>Evidence, not certification.</strong> This service analyses document structure. It is not audit assurance, legal advice, compliance certification, investment advice, or proof of greenwashing.</p>
    <h2>One workbench, two product families</h2>
    <div class="grid">
      <div class="card">
        <h3>ESG / Climate commitments</h3>
        <p>Extract commitments with page or paragraph evidence, then test observability, enforceability, and revisability.</p>
      </div>
      <div class="card">
        <h3>AI Alignment Revisability Audit</h3>
        <p>Review 28 written controls for alignment targets, revision authority, version history, rollback, affected-party safeguards, oversight, and technical-control evidence.</p>
        <p><a href="/ai-revisability-audit">Read the product scope, price, and claim boundary</a></p>
      </div>
    </div>
    <h2>Separate founding plans</h2>
    <div class="grid">
      <div class="card">
        <strong>ESG Commitment Audit</strong>
        <p>US$29/month · 100 audited documents · first 20 customer organizations.</p>
      </div>
      <div class="card">
        <strong>AI Alignment Revisability Audit</strong>
        <p>US$99/month · 100 policy or evidence-pack jobs · first 20 customer organizations.</p>
      </div>
    </div>
    <p>Each plan provides one organization and one shared API key. Policy documents may be up to 100 pages and 50 MB. Evidence-pack ZIPs may be up to 100 MB with at most 200 MB of uncompressed content. Raw uploads are deleted after success or final failure; hosted reports are retained for seven days. Both public offers include a 30-day no-questions-asked full refund.</p>
    <h2>How to start</h2>
    <ol>
      <li>Choose the ESG or AI product on Gumroad and keep the license key from the receipt.</li>
      <li><a href="/activate">Activate the ESG license</a> or <a href="/ai-revisability-audit/activate">activate the AI license</a> to receive a one-time API key.</li>
      <li>Paste the API key into the <a href="/workspace">workbench</a>, choose a mode, and upload a document.</li>
    </ol>
    <p class="notice"><strong>Product boundary.</strong> The AI policy mode audits written governance structure and submitted evidence only. It does not assess the personality or rights of an individual and must not be used for employment, education, credit, immigration, insurance, political, or judicial decisions.</p>
    <p class="muted">Theory source for the revision-oriented framing:
      <a href="https://doi.org/10.5281/zenodo.24217876" rel="noopener">Xue, Z. (2026), <em>On Recursive Freedom: A Theory of the Freedom to Revise</em>, DOI 10.5281/zenodo.24217876</a>.
      The software applies this idea only to documented policy structure, not to the freedom or conduct of any individual.</p>
    <h2>Developer interface</h2>
    <p>Health endpoint: <a href="/v1/health">/v1/health</a>. Source code and rules:
      <a href="https://github.com/franka328162810-cell/esg-commitment-audit">GitHub</a>.</p>
    <nav>
      <a href="/workspace">Workbench</a>
      <a href="/privacy">Privacy draft</a>
      <a href="/terms">Terms draft</a>
      <a href="mailto:franka328162810@gmail.com">Support</a>
    </nav>
    <p class="muted">Operator: Xue Zhi Xin (ICS-TEC). Last updated: 2026-11-23.</p>
  </article>`,
  "en",
);

export const recursiveFreedomPage = page(
  "Recursive Freedom Audit for AI | ICS-TEC",
  `<article>
    <p class="eyebrow">ICS-TEC / AI GOVERNANCE REVIEW</p>
    <h1>Can an AI policy be revised without locking people in?</h1>
    <p>Recursive Freedom Audit for AI reviews the written revision architecture of AI policies, model cards, and governance documents. It shows whether the document identifies who can change the rules, when they are reviewed, how changes are communicated, and whether affected people have appeal, refusal, and exit routes.</p>
    <div class="actions">
      <a class="button" href="/workspace">Run an audit in the workbench</a>
      <a class="button secondary" href="/recursive-freedom/sample">Open a public sample report</a>
      <a class="button secondary" href="https://icsstudies.gumroad.com/l/esg-commitment-audit" rel="noopener">Access the Founding plan</a>
    </div>
    <p class="notice"><strong>Scope boundary.</strong> This product checks written governance structure. It does not establish legal compliance, safety, truthfulness, or the actual behavior of an AI system. It does not score an individual person's psychology, political views, employability, creditworthiness, insurability, educational eligibility, immigration status, or legal culpability.</p>

    <h2>What the audit checks</h2>
    <div class="grid">
      <div class="card"><strong>Authority and traceability</strong><p>Scope, effective date, accountable owner, review cadence, revision authority, and version history.</p></div>
      <div class="card"><strong>People and recourse</strong><p>Advance notice, appeal, human review, refusal, opt-out, exit, and future-resident protection.</p></div>
      <div class="card"><strong>Recoverability</strong><p>Monitoring evidence, audit logs, rollback, suspension, deprecation, and independent oversight.</p></div>
    </div>
    <ol>
      <li>Scope and accountable owner</li>
      <li>Review cadence</li>
      <li>Revision authority and process</li>
      <li>Version history and change log</li>
      <li>Advance notice</li>
      <li>Appeal and human review</li>
      <li>Refusal, opt-out, and exit</li>
      <li>Monitoring, audit logs, and evidence</li>
      <li>Rollback, suspension, and deprecation</li>
      <li>Independent oversight</li>
    </ol>

    <h2>Current validation record</h2>
    <p>The v0.2 rule set was tested against five public AI policies or governance documents: OpenAI Usage Policies, Anthropic Usage Policy, Google Generative AI Prohibited Use Policy, Anthropic Responsible Scaling Policy, and Google DeepMind's Frontier Safety Framework introduction.</p>
    <div class="table-wrap">
      <table class="data-table">
        <thead><tr><th>Document</th><th>Present</th><th>Partial</th><th>Missing</th></tr></thead>
        <tbody>
          <tr><td>OpenAI Usage Policies</td><td>2</td><td>5</td><td>3</td></tr>
          <tr><td>Anthropic Usage Policy</td><td>0</td><td>4</td><td>6</td></tr>
          <tr><td>Google Generative AI Prohibited Use Policy</td><td>0</td><td>1</td><td>9</td></tr>
          <tr><td>Anthropic Responsible Scaling Policy</td><td>2</td><td>4</td><td>4</td></tr>
          <tr><td>Google DeepMind Frontier Safety Framework introduction</td><td>0</td><td>1</td><td>9</td></tr>
        </tbody>
      </table>
    </div>
    <p>Across 50 check-level decisions, the current rule set matched the written adjudication in 50 cases. The review found 19 positive or partial controls, with zero recorded false positives and zero recorded false negatives under the adjudication method.</p>
    <p class="notice"><strong>Validation limit.</strong> This is a five-document internal development benchmark reviewed by Codex under written rules. It is not an independent external validation or an assurance opinion. The rules were refined after reviewing initial false positives, so the sample is not a fully held-out test. Missing means the examined text did not contain supporting evidence; it does not prove that the organization lacks an internal practice.</p>

    <h2>What the statuses mean</h2>
    <div class="table-wrap">
      <table class="data-table">
        <thead><tr><th>Status</th><th>Meaning</th></tr></thead>
        <tbody>
          <tr><td><span class="status-pill status-present">present</span></td><td>The text contains the relevant structural control and source evidence.</td></tr>
          <tr><td><span class="status-pill status-partial">partial</span></td><td>Some supporting language is present, but a material element is absent or incomplete.</td></tr>
          <tr><td><span class="status-pill status-missing">missing</span></td><td>No supporting evidence was located in the examined document.</td></tr>
        </tbody>
      </table>
    </div>

    <h2>Commercial status</h2>
    <p>AI Alignment Revisability Audit is a separate US$99/month founding subscription for the first 20 customer organizations. It includes 100 policy or evidence-pack jobs per month, one organization, one shared API key, and a 30-day no-questions-asked full refund. Policy documents may be up to 100 pages and 50 MB; evidence-pack ZIPs may be up to 100 MB with at most 200 MB of uncompressed content.</p>
    <p>Planned layers are separate products rather than duplicate names:</p>
    <ul>
      <li><strong>AI Alignment Revisability Audit:</strong> the current document and evidence-pack review described on this page.</li>
      <li><strong>AI Public Commitment & Revision Monitor:</strong> a future independent data product that tracks public policy changes over time.</li>
      <li><strong>Organizational Revisability Audit:</strong> a future professional service that tests actual governance, appeals, exit paths, and continuity, not only text.</li>
    </ul>

    <h2>Theory source</h2>
    <p>The revision-oriented framing is informed by <a href="https://doi.org/10.5281/zenodo.24217876" rel="noopener">Xue, Z. (2026), <em>On Recursive Freedom: A Theory of the Freedom to Revise</em></a>. The publication identifies intellectual provenance. It is not evidence that this rule engine has been independently validated.</p>
    <nav>
      <a href="/">Home</a>
      <a href="/workspace">Workbench</a>
      <a href="https://github.com/franka328162810-cell/esg-commitment-audit/blob/main/docs/METHODOLOGY.md" rel="noopener">Methodology</a>
      <a href="mailto:franka328162810@gmail.com">Support</a>
    </nav>
  </article>`,
  "en",
);

export const recursiveFreedomSamplePage = page(
  "Public sample | Recursive Freedom Audit for AI",
  `<article>
    <p class="eyebrow">ICS-TEC / PUBLIC SAMPLE</p>
    <h1>Recursive Freedom Audit sample</h1>
    <p><strong>Source reviewed:</strong> Anthropic's public Responsible Scaling Policy overview page. <a href="https://www.anthropic.com/responsible-scaling-policy" rel="noopener">Open the source</a>.</p>
    <p><strong>Information cut-off:</strong> 22 November 2026. <strong>Method:</strong> RFP-AI-policy-structure-v0.2. <strong>Report:</strong> 0.3.1.</p>
    <p class="notice"><strong>Read this correctly.</strong> This sample audits the structure of one public overview page, not the full linked policy, internal controls, or actual conduct. Missing means the examined text did not provide evidence. It does not prove that Anthropic lacks an internal practice.</p>

    <div class="grid">
      <div class="card"><strong>2</strong><br>Present</div>
      <div class="card"><strong>4</strong><br>Partial</div>
      <div class="card"><strong>4</strong><br>Missing</div>
    </div>

    <div class="table-wrap">
      <table class="data-table">
        <thead><tr><th>Check</th><th>Status</th><th>Evidence and finding</th></tr></thead>
        <tbody>
          <tr>
            <td>Scope and accountable owner</td>
            <td><span class="status-pill status-missing">missing</span></td>
            <td>The reviewed overview does not combine applicability, effective scope, and an accountable policy owner in one complete statement.</td>
          </tr>
          <tr>
            <td>Review cadence</td>
            <td><span class="status-pill status-partial">partial</span></td>
            <td>"We have ... made two minor updates to the text of the Responsible Scaling Policy, updating it to version 3.1." Updates are shown, but no scheduled review cadence is stated.</td>
          </tr>
          <tr>
            <td>Revision authority and process</td>
            <td><span class="status-pill status-partial">partial</span></td>
            <td>The version update process is visible, but the page does not state who may propose, approve, or veto changes.</td>
          </tr>
          <tr>
            <td>Version history and change log</td>
            <td><span class="status-pill status-present">present</span></td>
            <td>"We expect to make further changes, all of which will be logged both on this page and in a changelog in the policy document itself."</td>
          </tr>
          <tr>
            <td>Advance notice</td>
            <td><span class="status-pill status-partial">partial</span></td>
            <td>"We ... will use this page to inform the public of any developments." The page promises updates, but not advance notice before a material change.</td>
          </tr>
          <tr>
            <td>Appeal and human review</td>
            <td><span class="status-pill status-missing">missing</span></td>
            <td>No appeal route or policy-enforcement human-review process was located in the examined overview.</td>
          </tr>
          <tr>
            <td>Refusal, opt-out, and exit</td>
            <td><span class="status-pill status-missing">missing</span></td>
            <td>No affected-person refusal, opt-out, or exit route was located.</td>
          </tr>
          <tr>
            <td>Monitoring, audit logs, and evidence</td>
            <td><span class="status-pill status-partial">partial</span></td>
            <td>"Asynchronous monitoring classifiers for a more detailed analysis of the completions for threats." Monitoring is present; audit-log access, retention, and governance are incomplete.</td>
          </tr>
          <tr>
            <td>Rollback, suspension, and deprecation</td>
            <td><span class="status-pill status-missing">missing</span></td>
            <td>No rule for rollback, suspension, or deprecation of the policy or affected system was located.</td>
          </tr>
          <tr>
            <td>Independent oversight</td>
            <td><span class="status-pill status-present">present</span></td>
            <td>"External review of our Risk Reports can involve multiple external reviewers..." The source states an external-review mechanism.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <p class="notice"><strong>Interpretation boundary.</strong> This sample is not legal advice, an assurance opinion, a safety certification, or a conclusion about Anthropic's internal governance. It demonstrates how the rule engine exposes written evidence, partial controls, and omissions.</p>
    <nav>
      <a href="/recursive-freedom">Product overview</a>
      <a href="/workspace">Run your own audit</a>
      <a href="/">Home</a>
    </nav>
  </article>`,
  "en",
);

export const aiRevisabilityPage = page(
  "AI Alignment Revisability Audit | ICS-TEC",
  `<article>
    <p class="eyebrow">ICS-TEC / AI ALIGNMENT REVISABILITY</p>
    <h1>Can an AI system's rules be changed, challenged, and reversed?</h1>
    <p>AI Alignment Revisability Audit reviews the written authorities, revision routes, version history, rollback controls, oversight, and affected-party safeguards around an AI policy, constitution, model card, or governance framework.</p>
    <div class="actions">
      <a class="button" href="https://icsstudies.gumroad.com/l/ai-alignment-revisability-audit" rel="noopener">View the founding plan on Gumroad</a>
      <a class="button secondary" href="/ai-revisability-audit/activate">Activate a purchased license</a>
      <a class="button secondary" href="/workspace?mode=ai-revisability">Open the hosted workbench</a>
      <a class="button secondary" href="/ai-revisability-audit/sample">Open a public sample</a>
      <a class="button secondary" href="https://github.com/franka328162810-cell/esg-commitment-audit/blob/main/docs/AI_ALIGNMENT_REVISABILITY_AUDIT.md" rel="noopener">Read the method</a>
    </div>
    <p class="notice"><strong>Scope boundary.</strong> This is a document and evidence review, not a model safety test, legal-compliance finding, certification, measurement of hidden intent, or proof that an AI system is aligned.</p>

    <h2>What the audit reviews</h2>
    <div class="grid">
      <div class="card"><strong>Targets and authority</strong><p>Alignment targets, normative hierarchy, accountable owners, revision authority, conflict resolution, and stakeholder participation.</p></div>
      <div class="card"><strong>Revision and rollback</strong><p>Review cadence, change triggers, gradual deployment, version history, prior-version retention, rollback authority, exercises, and protected clauses.</p></div>
      <div class="card"><strong>People and evidence</strong><p>Notice, explanation, appeal, human review, refusal, exit, monitoring, audit logs, retention, oversight, anti-abuse controls, capability gates, and interruption.</p></div>
    </div>

    <h2>Industry profiles</h2>
    <div class="table-wrap">
      <table class="data-table">
        <thead><tr><th>Profile</th><th>Additional controls</th></tr></thead>
        <tbody>
          <tr><td>General AI governance</td><td>28 core written controls.</td></tr>
          <tr><td>News media</td><td>Content provenance and editorial correction or retraction.</td></tr>
          <tr><td>Advertising</td><td>Client disclosure and rights, consent, and usage evidence.</td></tr>
          <tr><td>Insurance</td><td>Adverse-action explanation and independent human review.</td></tr>
          <tr><td>Industrial design</td><td>Design-artifact provenance and design-freeze/release control.</td></tr>
        </tbody>
      </table>
    </div>

    <h2>Evidence grades</h2>
    <p>The review distinguishes <strong>absent</strong>, <strong>asserted only</strong>, <strong>documented</strong>, <strong>contradicted</strong>, <strong>operationally evidenced</strong>, and <strong>independently verified</strong> controls. The hosted text engine currently establishes text evidence; operation records and independent verification require separate artifacts and human review.</p>

    <h2>Continuous review</h2>
    <p>Single documents can be compared with a previous version and a sealed evidence pack can be uploaded to verify dates, issuers, hashes, artifact compatibility, and proposed E2/E3/E4 grade upgrades. Every operational or independent grade proposal requires human confirmation.</p>

    <h2>Commercial plan</h2>
    <p>The AI Alignment Revisability Audit is a separate <strong>US$99/month</strong> founding subscription supplied through Gumroad. It includes one organization, one shared API key, up to 100 audited policy or evidence-pack jobs per month, 100 pages and 50 MB per policy document, a 100 MB evidence-pack ZIP containing at most 200 MB of uncompressed content, and seven-day hosted report retention. The founding price is limited to the first 20 customer organizations. A full refund is available within 30 days of the initial purchase.</p>
    <p>The local CLI, benchmark and evidence-pack implementation remain open source under the repository licences.</p>

    <h2>Validation</h2>
    <p>The frozen 2026-11-23 multi-jurisdiction benchmark covers 21 documents and 588 control decisions, including the EU AI Act, current UK regulations, US federal actions and enacted US state AI laws. It is a single-reviewer written adjudication, not an independent blinded validation.</p>

    <nav>
      <a href="/">Home</a>
      <a href="/workspace">Workbench</a>
      <a href="/privacy">Privacy draft</a>
      <a href="/terms">Terms draft</a>
      <a href="mailto:franka328162810@gmail.com">Support</a>
    </nav>
  </article>`,
  "en",
);

export const aiRevisabilitySamplePage = page(
  "Public sample | AI Alignment Revisability Audit",
  `<article>
    <p class="eyebrow">ICS-TEC / SYNTHETIC PUBLIC SAMPLE</p>
    <h1>AI Alignment Revisability Audit sample</h1>
    <p><strong>Source:</strong> a synthetic AI governance policy created to demonstrate a complete written control structure. <a href="https://github.com/franka328162810-cell/esg-commitment-audit/blob/main/examples/revisability_strong_policy.md" rel="noopener">Open the sample source</a>.</p>
    <p><strong>Method:</strong> RFP-AI-revisability-document-v0.2. <strong>Profile:</strong> General AI governance.</p>
    <p class="notice"><strong>Read this correctly.</strong> This is not a real organisation, an independent validation, or evidence that any control operates in practice. The sample deliberately contains supporting language for all 28 core checks.</p>

    <div class="grid">
      <div class="card"><strong>28</strong><br>Checks</div>
      <div class="card"><strong>28</strong><br>Documented controls</div>
      <div class="card"><strong>0</strong><br>Absent or contradicted</div>
    </div>

    <div class="table-wrap">
      <table class="data-table">
        <thead><tr><th>Dimension</th><th>Representative written evidence</th></tr></thead>
        <tbody>
          <tr><td>Alignment target and hierarchy</td><td>Named constitution, redlines, precedence, and conflict adjudication.</td></tr>
          <tr><td>Authority and participation</td><td>Policy owner, revision procedure, approval board, and public consultation.</td></tr>
          <tr><td>Revisionability</td><td>Annual review, incident triggers, staged rollout, success criteria, and stop conditions.</td></tr>
          <tr><td>Version traceability</td><td>Semantic version, dated change log, archive, and forward-version rollback rule.</td></tr>
          <tr><td>Reversibility and rollback</td><td>Rollback thresholds, authority, exercises, protected clauses, and independent review.</td></tr>
          <tr><td>Affected people</td><td>Advance notice, plain-language explanation, appeal, human review, opt-out, and exit.</td></tr>
          <tr><td>Monitoring and oversight</td><td>Metrics, append-only logs, retention, external audit, anti-abuse controls, and uncertainty handling.</td></tr>
          <tr><td>Technical controls</td><td>Deployment gate, named approval, stop condition, kill switch, shutdown, and interruption testing.</td></tr>
        </tbody>
      </table>
    </div>

    <p class="notice"><strong>Interpretation boundary.</strong> Text evidence demonstrates that a control is written down. It does not prove that the control operated, was independently reviewed, or made the AI system safe.</p>
    <nav>
      <a href="/ai-revisability-audit">Product overview</a>
      <a href="/workspace">Run your own audit</a>
      <a href="/">Home</a>
    </nav>
  </article>`,
  "en",
);

export const workspacePage = page(
  "Evidence Workbench | ESG Commitment Audit",
  `<article>
    <p class="eyebrow">ICS-TEC / EVIDENCE WORKBENCH</p>
    <h1>Run and review an audit</h1>
    <p>Your API key stays in this browser tab's session storage and is removed when the tab closes. Documents are uploaded over HTTPS to your ICS account.</p>
    <p class="notice"><strong>Quota note:</strong> each completed job uses one document from the monthly allowance. Deleting a report removes stored output but does not restore quota.</p>

    <section aria-labelledby="account-heading">
      <h2 id="account-heading">1. Connect your account</h2>
      <div id="connected-row" hidden>
        <div id="account-summary" class="success" aria-live="polite"></div>
        <div class="actions">
          <button id="forget-key" class="button secondary" type="button">Forget key from this tab</button>
          <a class="button secondary" href="/activate">Activate another license</a>
        </div>
      </div>
      <form id="connect-form">
        <label for="api-key">ICS API key</label>
        <div class="field-row">
          <input id="api-key" type="password" autocomplete="off" spellcheck="false" placeholder="esg_live_..." required>
          <button id="connect-button" class="button" type="submit">Connect</button>
        </div>
        <p class="muted">Need a key? Activate an <a href="/activate">ESG Gumroad license</a> or an <a href="/ai-revisability-audit/activate">AI Gumroad license</a>.</p>
      </form>
      <p id="account-message" class="status" aria-live="polite"></p>
    </section>

    <section aria-labelledby="mode-heading">
      <h2 id="mode-heading">2. Choose an evidence mode</h2>
      <div class="grid">
        <label class="mode-card">
          <input type="radio" name="audit-mode" value="commitment" checked>
          <strong>ESG / Climate Commitments</strong>
          <span class="muted">Extraction, source evidence, and CRV structure checks.</span>
        </label>
        <label class="mode-card">
          <input type="radio" name="audit-mode" value="ai-revisability">
          <strong>AI Alignment Revisability Audit</strong>
          <span class="muted">Twenty-eight written controls for authority, revision, rollback, affected people, evidence, and oversight.</span>
        </label>
        <label class="mode-card">
          <input type="radio" name="audit-mode" value="evidence-pack">
          <strong>AI Revisability Evidence Pack</strong>
          <span class="muted">Verify a sealed ZIP manifest and propose human-confirmed E2, E3, or E4 upgrades.</span>
        </label>
      </div>
      <p id="mode-note" class="muted"></p>
      <p class="muted"><a href="/ai-revisability-audit">Read the AI Alignment Revisability Audit scope and claim boundary</a></p>
      <p class="muted">The product's revision-oriented framing is informed by
        <a href="https://doi.org/10.5281/zenodo.24217876" rel="noopener">On Recursive Freedom (2026), DOI 10.5281/zenodo.24217876</a>.
        This is not a psychological or personal-rights assessment.</p>
      <p id="weight-field">
        <label for="weights">ESG weighting preset</label>
        <select id="weights">
          <option value="default">Default: balanced</option>
          <option value="obs-priority">Prioritise observability</option>
          <option value="enf-priority">Prioritise enforceability</option>
          <option value="rev-priority">Prioritise revisability</option>
          <option value="esg-balanced">ESG-balanced</option>
        </select>
      </p>
      <p id="profile-field" hidden>
        <label for="review-profile">AI review profile</label>
        <select id="review-profile">
          <option value="general">General AI governance</option>
          <option value="news_media">News media</option>
          <option value="advertising">Advertising services</option>
          <option value="insurance">Insurance</option>
          <option value="industrial_design">Industrial design</option>
        </select>
      </p>
    </section>

    <section aria-labelledby="upload-heading">
      <h2 id="upload-heading">3. Upload a document</h2>
      <div id="dropzone" class="dropzone" role="button" tabindex="0" aria-controls="file-input">
        <strong>Drop a file here or click to choose</strong>
        <p id="file-help" class="muted">PDF with a text layer, DOCX, TXT, or Markdown · maximum 50 MB · maximum 100 pages</p>
        <p id="selected-file" class="muted">No file selected.</p>
      </div>
      <input id="file-input" type="file" accept=".pdf,.docx,.txt,.md,.markdown" hidden>
      <div class="actions">
        <button id="run-button" class="button" type="button">Run audit</button>
        <button id="cancel-current" class="button secondary" type="button" hidden>Delete current job</button>
      </div>
      <p id="run-status" class="status" aria-live="polite"></p>
      <div id="error-box" class="error" role="alert" hidden></div>
    </section>

    <section id="report-section" class="report" aria-labelledby="report-heading" hidden>
      <div class="actions">
        <h2 id="report-heading">Audit report</h2>
        <button id="download-json" class="button secondary" type="button">Download JSON</button>
        <button id="download-csv" class="button secondary" type="button">Download CSV</button>
        <button id="delete-report" class="button danger" type="button">Delete report</button>
      </div>
      <div id="report-content"></div>
    </section>

    <nav>
      <a href="/">Home</a>
      <a href="/privacy">Privacy draft</a>
      <a href="/terms">Terms draft</a>
      <a href="mailto:franka328162810@gmail.com">Support</a>
    </nav>
  </article>
  <script>
    const STORAGE_KEY = "esg_commitment_audit_api_key";
    const MAX_DOCUMENT_BYTES = 50 * 1024 * 1024;
    const MAX_EVIDENCE_PACK_BYTES = 100 * 1024 * 1024;
    const SUPPORTED_DOCUMENT = /\\.(pdf|docx|txt|md|markdown)$/i;
    const SUPPORTED_EVIDENCE_PACK = /\\.zip$/i;
    const $ = (id) => document.getElementById(id);
    const connectForm = $("connect-form");
    const apiKeyInput = $("api-key");
    const connectButton = $("connect-button");
    const connectedRow = $("connected-row");
    const accountMessage = $("account-message");
    const accountSummary = $("account-summary");
    const selectedFileLabel = $("selected-file");
    const fileInput = $("file-input");
    const fileHelp = $("file-help");
    const dropzone = $("dropzone");
    const runButton = $("run-button");
    const runStatus = $("run-status");
    const errorBox = $("error-box");
    const reportSection = $("report-section");
    const reportContent = $("report-content");
    const cancelCurrent = $("cancel-current");
    const weightField = $("weight-field");
    const profileField = $("profile-field");
    const reviewProfile = $("review-profile");
    const modeNote = $("mode-note");
    let apiKey = sessionStorage.getItem(STORAGE_KEY) || "";
    let selectedFile = null;
    let currentJobId = null;
    let currentReport = null;
    let pollGeneration = 0;
    let accountAllowedModes = null;

    function escapeHtml(value) {
      return String(value == null ? "" : value).replace(/[&<>"']/g, (character) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
      })[character]);
    }

    function selectedMode() {
      const checked = document.querySelector('input[name="audit-mode"]:checked');
      return checked ? checked.value : "commitment";
    }

    function sleep(milliseconds) {
      return new Promise((resolve) => setTimeout(resolve, milliseconds));
    }

    function setMessage(element, message, isError) {
      element.textContent = message || "";
      element.hidden = !message;
      element.className = isError ? "error" : "success";
    }

    function clearError() {
      errorBox.textContent = "";
      errorBox.hidden = true;
    }

    function showError(message) {
      errorBox.textContent = message;
      errorBox.hidden = false;
    }

    async function responsePayload(response) {
      const text = await response.text();
      if (!text) return {};
      try {
        return JSON.parse(text);
      } catch {
        return { error: text };
      }
    }

    function errorMessage(payload, status) {
      if (payload && payload.error) return String(payload.error);
      if (status === 401) return "The API key is invalid or expired.";
      if (status === 411) return "The browser did not provide a file length. Try a current browser.";
      if (status === 413) return "The file exceeds the upload or page limit.";
      if (status === 429) return "The monthly document quota is exhausted.";
      return "Request failed with HTTP " + status + ".";
    }

    async function apiFetch(path, options) {
      const headers = new Headers((options && options.headers) || {});
      if (apiKey) headers.set("Authorization", "Bearer " + apiKey);
      const response = await fetch(path, Object.assign({}, options || {}, { headers }));
      if (response.status === 401) {
        forgetKey(false);
        throw new Error("The API key is invalid or expired. Connect again.");
      }
      return response;
    }

    function renderAccount(account) {
      accountAllowedModes = Array.isArray(account.allowed_audit_modes)
        ? account.allowed_audit_modes
        : null;
      accountSummary.innerHTML =
        "<strong>" + escapeHtml(account.name) + "</strong><br>" +
        "Plan: " + escapeHtml(account.plan) + " · " +
        escapeHtml(account.documents_used) + " / " +
        escapeHtml(account.monthly_document_limit) + " documents used in " +
        escapeHtml(account.usage_period) + " · " +
        escapeHtml(account.remaining_documents) + " remaining";
      connectedRow.hidden = false;
      connectForm.hidden = true;
      apiKeyInput.value = "";
      applyModeAvailability();
    }

    function applyModeAvailability() {
      const inputs = Array.from(document.querySelectorAll('input[name="audit-mode"]'));
      inputs.forEach((input) => {
        input.disabled = Boolean(
          accountAllowedModes && !accountAllowedModes.includes(input.value)
        );
      });
      const current = document.querySelector('input[name="audit-mode"]:checked');
      if (current && current.disabled) {
        const firstEnabled = inputs.find((input) => !input.disabled);
        if (firstEnabled) firstEnabled.checked = true;
      }
      updateMode();
    }

    async function loadAccount() {
      const response = await apiFetch("/v1/account", { method: "GET" });
      const payload = await responsePayload(response);
      if (!response.ok) throw new Error(errorMessage(payload, response.status));
      renderAccount(payload);
      setMessage(accountMessage, "", false);
      return payload;
    }

    function forgetKey(showMessage) {
      apiKey = "";
      sessionStorage.removeItem(STORAGE_KEY);
      connectedRow.hidden = true;
      connectForm.hidden = false;
      reportSection.hidden = true;
      currentReport = null;
      currentJobId = null;
      pollGeneration += 1;
      accountAllowedModes = null;
      applyModeAvailability();
      if (showMessage) setMessage(accountMessage, "API key removed from this tab.", false);
    }

    async function connectWithKey(candidate) {
      const key = String(candidate || "").trim();
      if (!/^(?:esg|ai)_live_/.test(key)) {
        setMessage(accountMessage, "Enter a valid ICS API key beginning with esg_live_ or ai_live_.", true);
        return;
      }
      connectButton.disabled = true;
      setMessage(accountMessage, "Checking account...", false);
      apiKey = key;
      try {
        await loadAccount();
        sessionStorage.setItem(STORAGE_KEY, key);
        setMessage(accountMessage, "Connected.", false);
      } catch (error) {
        apiKey = "";
        setMessage(accountMessage, error.message || String(error), true);
      } finally {
        connectButton.disabled = false;
      }
    }

    function chooseFile(file) {
      clearError();
      if (!file) return;
      const evidencePack = selectedMode() === "evidence-pack";
      const supported = evidencePack ? SUPPORTED_EVIDENCE_PACK : SUPPORTED_DOCUMENT;
      const maxBytes = evidencePack ? MAX_EVIDENCE_PACK_BYTES : MAX_DOCUMENT_BYTES;
      if (!supported.test(file.name)) {
        showError(evidencePack
          ? "Choose a ZIP evidence pack."
          : "Choose a PDF, DOCX, TXT, or Markdown file.");
        return;
      }
      if (file.size > maxBytes) {
        showError(
          "The file exceeds the " + (evidencePack ? "100 MB" : "50 MB") + " limit."
        );
        return;
      }
      selectedFile = file;
      const fileSize = file.size < 1024 * 1024
        ? (file.size / 1024).toFixed(1) + " KB"
        : (file.size / 1024 / 1024).toFixed(2) + " MB";
      selectedFileLabel.textContent =
        file.name + " · " + fileSize;
    }

    function updateMode() {
      const mode = selectedMode();
      const evidencePack = mode === "evidence-pack";
      weightField.hidden = mode !== "commitment";
      profileField.hidden = mode !== "ai-revisability";
      fileInput.accept = evidencePack ? ".zip" : ".pdf,.docx,.txt,.md,.markdown";
      fileHelp.textContent = evidencePack
        ? "ZIP containing one manifest.yaml plus policy and evidence files · maximum 100 MB compressed and 200 MB uncompressed"
        : "PDF with a text layer, DOCX, TXT, or Markdown · maximum 50 MB · maximum 100 pages";
      selectedFile = null;
      fileInput.value = "";
      selectedFileLabel.textContent = "No file selected.";
      modeNote.textContent = mode === "ai-revisability"
        ? "Reviews 28 core written controls plus profile-specific safeguards. It reviews documents and evidence, not an AI system's actual behaviour."
        : evidencePack
          ? "Verifies declared hashes, dates, issuers, artifact compatibility, and proposes evidence-grade upgrades for human confirmation."
          : "Commitment mode extracts ESG and climate promises and scores their written structure.";
    }

    function positionLabel(evidence) {
      if (!evidence) return "position unavailable";
      if (evidence.page_number != null) return "page " + evidence.page_number;
      return "paragraph " + evidence.paragraph_index;
    }

    function evidenceBlocks(evidence) {
      if (!evidence || !evidence.length) {
        return '<p class="muted">No supporting text located.</p>';
      }
      return evidence.map((item) =>
        '<div class="evidence"><p>' + escapeHtml(item.excerpt || item.text) +
        '</p><p class="muted">' + escapeHtml(positionLabel(item)) +
        (item.section ? " · " + escapeHtml(item.section) : "") +
        '</p></div>'
      ).join("");
    }

    function reportHeader(report) {
      const reportLabel = report.report_type === "recursive-freedom"
        ? "Recursive Freedom Audit for AI"
        : report.report_type === "ai-alignment-revisability"
          ? "AI Alignment Revisability Audit"
          : "ESG / Climate Commitment Audit";
      return '<div class="card"><p class="eyebrow">' +
        escapeHtml(reportLabel) +
        '</p><h2>' + escapeHtml(report.document.filename) + '</h2>' +
        '<p class="muted">Generated ' + escapeHtml(report.generated_at) +
        ' · SHA-256 ' + escapeHtml(report.document.sha256) + '</p></div>';
    }

    function renderGovernanceReport(report) {
      const summary = report.summary;
      let html = reportHeader(report);
      html += '<div class="grid">';
      html += '<div class="card"><strong>' + escapeHtml(summary.present_count) + '</strong><br>Present</div>';
      html += '<div class="card"><strong>' + escapeHtml(summary.partial_count) + '</strong><br>Partial</div>';
      html += '<div class="card"><strong>' + escapeHtml(summary.missing_count) + '</strong><br>Missing</div>';
      html += '</div>';
      if (summary.document_warnings && summary.document_warnings.length) {
        html += '<div class="notice"><strong>Risk language found</strong><ul>' +
          summary.document_warnings.map((item) => '<li>' + escapeHtml(item) + '</li>').join("") +
          '</ul></div>';
      }
      html += report.checks.map((check) =>
        '<div class="report-card"><p><span class="status-pill status-' + escapeHtml(check.status) + '">' +
        escapeHtml(check.status) + '</span></p><h3>' + escapeHtml(check.label) +
        '</h3><p>' + escapeHtml(check.note) + '</p>' + evidenceBlocks(check.evidence) + '</div>'
      ).join("");
      if (report.recommendations && report.recommendations.length) {
        html += '<div class="card"><h3>Suggested next steps</h3><ul>' +
          report.recommendations.map((item) => '<li>' + escapeHtml(item) + '</li>').join("") +
          '</ul></div>';
      }
      html += '<div class="notice"><strong>Scope boundary</strong><p>' + escapeHtml(report.disclaimer) + '</p></div>';
      return html;
    }

    function renderRevisabilityReport(report) {
      const summary = report.summary;
      let html = reportHeader(report);
      html += '<div class="grid">';
      html += '<div class="card"><strong>' + escapeHtml(summary.check_count) + '</strong><br>Checks</div>';
      html += '<div class="card"><strong>' + escapeHtml(summary.documented_count) + '</strong><br>Documented</div>';
      html += '<div class="card"><strong>' + escapeHtml(summary.asserted_count) + '</strong><br>Asserted only</div>';
      html += '<div class="card"><strong>' + escapeHtml(summary.absent_count) + '</strong><br>Absent</div>';
      html += '<div class="card"><strong>' + escapeHtml(summary.contradicted_count) + '</strong><br>Contradicted</div>';
      html += '</div>';
      if (report.warnings && report.warnings.length) {
        html += '<div class="notice"><strong>Risk warnings</strong><ul>' +
          report.warnings.map((item) => '<li>' + escapeHtml(item) + '</li>').join("") +
          '</ul></div>';
      }
      html += (report.dimensions || []).map((dimension) => {
        const checks = (dimension.checks || []).map((check) => {
          const artifacts = check.required_artifacts && check.required_artifacts.length
            ? '<h4>Evidence still required</h4><ul>' +
              check.required_artifacts.map((item) => '<li>' + escapeHtml(item) + '</li>').join("") +
              '</ul>'
            : "";
          return '<div class="report-card"><p><span class="status-pill status-' +
            escapeHtml(check.grade) + '">' + escapeHtml(check.grade.replaceAll("_", " ")) +
            '</span></p><h3>' + escapeHtml(check.label) + '</h3><p>' +
            escapeHtml(check.rationale) + '</p>' + evidenceBlocks(check.evidence) +
            artifacts +
            (check.recommendation
              ? '<p class="muted"><strong>Recommendation:</strong> ' + escapeHtml(check.recommendation) + '</p>'
              : "") +
            '</div>';
        }).join("");
        return '<section><h2>' + escapeHtml(dimension.label) + '</h2>' + checks + '</section>';
      }).join("");
      if (report.recommendations && report.recommendations.length) {
        html += '<div class="card"><h3>Priority recommendations</h3><ul>' +
          report.recommendations.map((item) => '<li>' + escapeHtml(item) + '</li>').join("") +
          '</ul></div>';
      }
      if (report.evidence_requests && report.evidence_requests.length) {
        html += '<div class="card"><h3>Evidence request list</h3><ul>' +
          report.evidence_requests.map((item) => '<li>' + escapeHtml(item) + '</li>').join("") +
          '</ul></div>';
      }
      html += '<div class="notice"><strong>Claim boundary</strong><p>' +
        escapeHtml(report.disclaimer) + '</p></div>';
      return html;
    }

    function renderEvidencePackReport(report) {
      let html = '<div class="card"><p class="eyebrow">AI Revisability Evidence Pack</p>' +
        '<h2>' + escapeHtml(report.organization) + '</h2>' +
        '<p class="muted">Base document: ' + escapeHtml(report.base_document) +
        ' · generated ' + escapeHtml(report.generated_at) + '</p></div>';
      html += '<div class="grid">';
      html += '<div class="card"><strong>' + escapeHtml(report.artifact_inventory.length) + '</strong><br>Artifacts checked</div>';
      html += '<div class="card"><strong>' + escapeHtml(report.promotions.length) + '</strong><br>Grade proposals</div>';
      html += '<div class="card"><strong>' + escapeHtml(report.unresolved_controls.length) + '</strong><br>Remaining gaps</div>';
      html += '<div class="card"><strong>' + escapeHtml(report.warnings.length) + '</strong><br>Warnings</div>';
      html += '</div>';

      html += '<section><h2>Artifact inventory</h2>' +
        report.artifact_inventory.map((item) => {
          const hashStatus = item.hash_matches === true
            ? "matched"
            : item.hash_matches === false
              ? "mismatch"
              : "not pinned";
          return '<div class="report-card"><h3>' + escapeHtml(item.path) + '</h3>' +
            '<p><span class="status-pill">' + escapeHtml(item.artifact_type) +
            '</span> · issuer ' + escapeHtml(item.issuer || "missing") +
            ' · issued ' + escapeHtml(item.issued_at || "missing") +
            ' · hash ' + escapeHtml(hashStatus) + '</p>' +
            '<p class="muted">E3 eligible: ' +
            (item.eligible_for_operational_evidence ? "yes" : "no") +
            (item.warnings.length ? ' · ' + escapeHtml(item.warnings.join("; ")) : "") +
            '</p></div>';
        }).join("") + '</section>';

      html += '<section><h2>Proposed grade promotions</h2>' +
        (report.promotions.length
          ? report.promotions.map((item) =>
              '<div class="report-card"><h3>' + escapeHtml(item.check_key) + '</h3>' +
              '<p><span class="status-pill">' + escapeHtml(item.baseline_grade) +
              '</span> → <span class="status-pill">' + escapeHtml(item.proposed_grade) +
              '</span></p><p>' + escapeHtml(item.rationale) + '</p>' +
              '<p class="muted">Supporting artifacts: ' +
              escapeHtml(item.supporting_artifacts.join(", ")) + '</p>' +
              '<p class="muted"><strong>Human confirmation required:</strong> ' +
              (item.requires_human_confirmation ? "yes" : "no") + '</p></div>'
            ).join("")
          : '<p class="muted">No promotion was proposed.</p>') +
        '</section>';

      html += '<section><h2>Remaining evidence gaps</h2>' +
        (report.unresolved_controls.length
          ? '<ul>' + report.unresolved_controls.map((item) =>
              '<li><strong>' + escapeHtml(item.check_key) + '</strong> (' +
              escapeHtml(item.baseline_grade) + '): needs ' +
              escapeHtml(item.missing_artifact_types.join(", ")) + '</li>'
            ).join("") + '</ul>'
          : '<p class="muted">No mapped gap remains.</p>') +
        '</section>';

      if (report.warnings.length) {
        html += '<div class="notice"><strong>Warnings</strong><ul>' +
          report.warnings.map((item) => '<li>' + escapeHtml(item) + '</li>').join("") +
          '</ul></div>';
      }
      html += '<div class="notice"><strong>Claim boundary</strong><p>' +
        escapeHtml(report.disclaimer) + '</p></div>';
      return html;
    }

    function renderCommitmentReport(report) {
      const summary = report.summary;
      let html = reportHeader(report);
      html += '<div class="grid">';
      html += '<div class="card"><strong>' + escapeHtml(summary.commitment_count) + '</strong><br>Commitments detected</div>';
      html += '<div class="card"><strong>' +
        (summary.average_crv == null ? "N/A" : Number(summary.average_crv).toFixed(3)) +
        '</strong><br>Average CRV structure score</div>';
      html += '</div>';
      if (summary.document_warnings && summary.document_warnings.length) {
        html += '<div class="notice"><strong>Document warnings</strong><ul>' +
          summary.document_warnings.map((item) => '<li>' + escapeHtml(item) + '</li>').join("") +
          '</ul></div>';
      }
      html += report.commitments.map((item) => {
        const dimensions = (item.dimensions || []).map((dimension) =>
          '<li><strong>' + escapeHtml(dimension.label) + '</strong>: ' +
          Number(dimension.score).toFixed(3) + '</li>'
        ).join("");
        return '<div class="report-card"><h3>' + escapeHtml(item.commitment_id) +
          ' · ' + escapeHtml(item.subcategory) + '</h3>' +
          '<p><span class="status-pill">' + escapeHtml(item.category) +
          '</span> CRV <strong>' + Number(item.crv_score).toFixed(3) +
          '</strong> · ' + escapeHtml(item.grade) + '</p>' +
          evidenceBlocks([item.evidence]) +
          '<h4>Structure dimensions</h4><ul>' + dimensions + '</ul>' +
          (item.warnings && item.warnings.length
            ? '<h4>Warnings</h4><ul>' + item.warnings.map((warning) => '<li>' + escapeHtml(warning) + '</li>').join("") + '</ul>'
            : "") +
          (item.recommendations && item.recommendations.length
            ? '<h4>Suggested text improvements</h4><ul>' + item.recommendations.map((recommendation) => '<li>' + escapeHtml(recommendation) + '</li>').join("") + '</ul>'
            : "") +
          '</div>';
      }).join("");
      html += '<div class="notice"><strong>Scope boundary</strong><p>' + escapeHtml(report.disclaimer) + '</p></div>';
      return html;
    }

    function renderReport(report) {
      currentReport = report;
      reportContent.innerHTML = report.report_type === "recursive-freedom"
        ? renderGovernanceReport(report)
        : report.report_type === "ai-alignment-revisability"
          ? renderRevisabilityReport(report)
          : report.report_type === "ai-revisability-evidence-pack"
            ? renderEvidencePackReport(report)
          : renderCommitmentReport(report);
      reportSection.hidden = false;
      reportSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    async function pollJob(jobId, generation) {
      const started = Date.now();
      while (generation === pollGeneration && Date.now() - started < 10 * 60 * 1000) {
        await sleep(2500);
        if (generation !== pollGeneration) return;
        const response = await apiFetch("/v1/audits/" + encodeURIComponent(jobId), { method: "GET" });
        const job = await responsePayload(response);
        if (!response.ok) throw new Error(errorMessage(job, response.status));
        runStatus.textContent = "Job " + job.status + " · attempt " + job.attempts + " · elapsed " +
          Math.round((Date.now() - started) / 1000) + "s";
        if (job.status === "completed") {
          const reportResponse = await apiFetch(
            "/v1/audits/" + encodeURIComponent(jobId) + "/report",
            { method: "GET" }
          );
          const report = await responsePayload(reportResponse);
          if (!reportResponse.ok) throw new Error(errorMessage(report, reportResponse.status));
          renderReport(report);
          runStatus.textContent = "Audit complete.";
          cancelCurrent.hidden = false;
          await loadAccount();
          return;
        }
        if (job.status === "failed" || job.status === "cancelled") {
          throw new Error(job.error || "The audit did not complete.");
        }
      }
      if (generation === pollGeneration) {
        throw new Error("The audit is taking longer than expected. Keep this page open and retry later.");
      }
    }

    async function runAudit() {
      clearError();
      if (!apiKey) {
        showError("Connect your API key before running an audit.");
        return;
      }
      if (!selectedFile) {
        showError("Choose a document first.");
        return;
      }
      const mode = selectedMode();
      runButton.disabled = true;
      reportSection.hidden = true;
      currentReport = null;
      currentJobId = null;
      runStatus.textContent = "Uploading " + selectedFile.name + "...";
      try {
        const response = await apiFetch("/v1/audits", {
          method: "POST",
          headers: {
            "Content-Type": selectedFile.type || "application/octet-stream",
            "X-ESG-Filename": encodeURIComponent(selectedFile.name),
            "X-ESG-Weights": mode === "commitment" ? $("weights").value : "default",
            "X-ESG-Mode": mode,
            "X-ESG-Profile": mode === "ai-revisability" ? reviewProfile.value : "general"
          },
          body: selectedFile
        });
        const payload = await responsePayload(response);
        if (!response.ok) throw new Error(errorMessage(payload, response.status));
        currentJobId = payload.id;
        cancelCurrent.hidden = false;
        pollGeneration += 1;
        const generation = pollGeneration;
        runStatus.textContent = "Queued. The document will be processed asynchronously.";
        await pollJob(currentJobId, generation);
      } catch (error) {
        showError(error.message || String(error));
        runStatus.textContent = "Audit stopped.";
      } finally {
        runButton.disabled = false;
      }
    }

    async function deleteCurrentJob() {
      if (!currentJobId || !apiKey) return;
      if (!window.confirm("Delete this job and its stored report? This does not restore monthly quota.")) return;
      const response = await apiFetch(
        "/v1/audits/" + encodeURIComponent(currentJobId),
        { method: "DELETE" }
      );
      if (!response.ok) {
        const payload = await responsePayload(response);
        showError(errorMessage(payload, response.status));
        return;
      }
      pollGeneration += 1;
      currentJobId = null;
      currentReport = null;
      reportSection.hidden = true;
      cancelCurrent.hidden = true;
      runStatus.textContent = "Job and stored report deleted.";
      await loadAccount();
    }

    function downloadText(filename, text, contentType) {
      const blob = new Blob([text], { type: contentType });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(link.href), 1000);
    }

    function csvCell(value) {
      const text = String(value == null ? "" : value).replace(/"/g, '""');
      return '"' + text + '"';
    }

    function downloadJson() {
      if (!currentReport || !currentJobId) return;
      downloadText(currentJobId + ".json", JSON.stringify(currentReport, null, 2), "application/json");
    }

    function downloadCsv() {
      if (!currentReport || !currentJobId) return;
      const rows = [];
      if (currentReport.report_type === "ai-revisability-evidence-pack") {
        rows.push(["Mode", "Control", "Baseline", "Proposed", "Artifacts", "Human confirmation"]);
        currentReport.promotions.forEach((item) => {
          rows.push([
            "evidence-pack",
            item.check_key,
            item.baseline_grade,
            item.proposed_grade,
            item.supporting_artifacts.join("; "),
            item.requires_human_confirmation ? "required" : "no"
          ]);
        });
      } else if (currentReport.report_type === "recursive-freedom") {
        rows.push(["Mode", "Check", "Status", "Note", "Evidence", "Page or paragraph"]);
        currentReport.checks.forEach((check) => {
          const first = check.evidence && check.evidence[0];
          rows.push([
            "recursive-freedom",
            check.label,
            check.status,
            check.note,
            first ? first.excerpt || first.text : "",
            first ? positionLabel(first) : ""
          ]);
        });
      } else if (currentReport.report_type === "ai-alignment-revisability") {
        rows.push(["Mode", "Dimension", "Check", "Grade", "Rationale", "Evidence", "Page or paragraph"]);
        currentReport.dimensions.forEach((dimension) => {
          dimension.checks.forEach((check) => {
            const first = check.evidence && check.evidence[0];
            rows.push([
              "ai-revisability",
              dimension.label,
              check.label,
              check.grade,
              check.rationale,
              first ? first.excerpt || first.text : "",
              first ? positionLabel(first) : ""
            ]);
          });
        });
      } else {
        rows.push(["Mode", "Commitment ID", "Category", "Subcategory", "CRV", "Grade", "Evidence", "Page or paragraph"]);
        currentReport.commitments.forEach((item) => {
          rows.push([
            "commitment",
            item.commitment_id,
            item.category,
            item.subcategory,
            item.crv_score,
            item.grade,
            item.evidence ? item.evidence.excerpt || item.evidence.text : "",
            positionLabel(item.evidence)
          ]);
        });
      }
      const csv = rows.map((row) => row.map(csvCell).join(",")).join("\\r\\n");
      downloadText(currentJobId + ".csv", csv, "text/csv;charset=utf-8");
    }

    connectForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      await connectWithKey(apiKeyInput.value);
    });
    $("forget-key").addEventListener("click", () => forgetKey(true));
    document.querySelectorAll('input[name="audit-mode"]').forEach((input) =>
      input.addEventListener("change", updateMode)
    );
    dropzone.addEventListener("click", () => fileInput.click());
    dropzone.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        fileInput.click();
      }
    });
    fileInput.addEventListener("change", () => chooseFile(fileInput.files[0]));
    ["dragenter", "dragover"].forEach((name) =>
      dropzone.addEventListener(name, (event) => {
        event.preventDefault();
        dropzone.classList.add("active");
      })
    );
    ["dragleave", "drop"].forEach((name) =>
      dropzone.addEventListener(name, (event) => {
        event.preventDefault();
        dropzone.classList.remove("active");
      })
    );
    dropzone.addEventListener("drop", (event) => chooseFile(event.dataTransfer.files[0]));
    runButton.addEventListener("click", runAudit);
    cancelCurrent.addEventListener("click", deleteCurrentJob);
    $("delete-report").addEventListener("click", deleteCurrentJob);
    $("download-json").addEventListener("click", downloadJson);
    $("download-csv").addEventListener("click", downloadCsv);
    const requestedMode = new URLSearchParams(location.search).get("mode");
    if (requestedMode) {
      const requestedInput = document.querySelector(
        'input[name="audit-mode"][value="' + CSS.escape(requestedMode) + '"]'
      );
      if (requestedInput) requestedInput.checked = true;
    }
    updateMode();
    if (apiKey) {
      apiKeyInput.value = apiKey;
      loadAccount().catch((error) => {
        setMessage(accountMessage, error.message || String(error), true);
      });
    }
  </script>`,
  "en",
);

export const privacyPage = page(
  "隐私政策草案 | ESG Commitment Audit",
  `<article>
    <p class="eyebrow">隐私政策草案</p>
    <h1>我们如何处理数据</h1>
    <p class="notice"><strong>草案提示：</strong>本页是正式收费前的透明说明草案，不构成法律意见，正式商业运营前应由合格律师按实际经营主体、地区与支付方案复核。</p>
    <h2>1. 运营者与联系</h2>
    <p>运营者：Xue Zhi Xin (ICS-TEC)。隐私与删除请求：<a href="mailto:franka328162810@gmail.com">franka328162810@gmail.com</a>。</p>
    <h2>2. 处理的数据</h2>
    <ul>
      <li>用户上传的 TXT、Markdown、DOCX、PDF、证据包 ZIP，以及文件名、大小、哈希和内容类型。</li>
      <li>分析生成的承诺、分数、证据位置和报告。</li>
      <li>组织名称、套餐、用量、API Key 的不可逆哈希、前缀、任务状态和错误信息。</li>
      <li>开通付费后产生的支付平台客户、订阅和 Webhook 标识。我们不存储银行卡号或支付验证码。</li>
      <li>保障安全与排障所需的时间、区域、错误和性能日志。</li>
    </ul>
    <h2>3. 处理目的</h2>
    <p>用于执行用户请求的文本分析、生成报告、租户隔离、配额和计费、安全防护、故障排查、支持以及履行法定义务。未经单独同意，不将客户文件用于训练通用 AI 模型，也不出售客户数据。</p>
    <h2>4. 保留与删除</h2>
    <ul>
      <li>原始上传：成功处理或最终失败后立即删除。</li>
      <li>分析报告：默认 7 天后删除；用户可提前删除。</li>
      <li>任务元数据：计划保留 180 天后清理；安全或计费记录可能在法律允许的必要期限内保留。</li>
      <li>删除请求可能受司法、税务、反欺诈或安全保留义务限制。</li>
    </ul>
    <h2>5. 服务商与跨境处理</h2>
    <p>当前基础设施使用 Cloudflare（Workers、D1、R2、Queues、Containers）并在其全球网络中处理数据。交易、税费和订阅管理由 Gumroad 及其支付与结算服务商处理；ICS-TEC 不接收或存储银行卡号。上述服务商可能依其条款进行跨境处理。</p>
    <h2>6. 安全与控制</h2>
    <p>服务采用 HTTPS、租户隔离、API Key 哈希、私有对象存储、短期报告访问和用量限制。互联网服务不存在绝对安全，用户应保护 API Key，不上传无权处理的机密或高度敏感个人信息。</p>
    <h2>7. 用户权利</h2>
    <p>用户可请求访问、更正、导出或删除与其账户有关的个人数据，并可提出投诉。请使用账户关联邮箱发送请求；为防止冒用，我们可能要求合理验证。</p>
    <h2>8. 儿童与年龄</h2>
    <p>本服务面向机构和成年专业用户，不面向未成年人，也不得用于上传未成年人的敏感个人信息。</p>
    <h2>9. 更新</h2>
    <p>重大变更将通过服务页面或账户联系渠道提示。本页说明当前付费试点，尚未经过律师独立复核。</p>
    <nav><a href="/">返回首页</a><a href="/terms">服务条款草案</a></nav>
  </article>`,
);

export const termsPage = page(
  "服务条款草案 | ESG Commitment Audit",
  `<article>
    <p class="eyebrow">服务条款草案</p>
    <h1>使用本服务前请阅读</h1>
    <p class="notice"><strong>草案提示：</strong>本页不构成法律意见，也尚未经过律师独立复核。当前付费服务由 Xue Zhi Xin (ICS-TEC) 运营，并通过 Gumroad 收款。</p>
    <h2>1. 服务范围</h2>
    <p>ICS-TEC 提供 ESG Commitment Audit 与 AI Alignment Revisability Audit。前者对可持续与气候承诺文本做结构化抽取、评分和证据定位；后者审查 AI 政策、治理文件及用户提交的证据包。结果可能不完整或存在误判，必须由用户结合原文复核。</p>
    <h2>2. 不提供专业鉴证</h2>
    <p>本服务不是审计、鉴证、法律、税务、投资或合规认证服务，不构成对“漂绿”、违法或重大性的事实认定。用户不得把结果作为唯一决策依据，也不得对外声称获得 ICS-TEC 或第三方的认证。</p>
    <h2>3. 账户与 API Key</h2>
    <p>用户应提供真实、必要的账户信息，妥善保管 API Key，并对该凭据下发生的活动负责。发现泄露应立即停用并联系我们。一个组织的额度和报告不得用于规避租户限制。</p>
    <h2>4. 上传内容与授权</h2>
    <p>用户声明其拥有处理上传内容所需的权利和合法基础。不得上传违法内容、无权披露的商业秘密、支付凭证、身份证件、医疗记录或其他与承诺分析无关的高度敏感个人信息。用户授予的服务处理许可仅限于完成请求、安全和依法履约所必需的范围。</p>
    <h2>5. 可接受使用</h2>
    <p>不得攻击、绕过配额、探测其他租户、传播恶意文件、自动生成误导性审计结论、侵犯知识产权或违反适用法律。我们可暂停高风险账户并保留依法报告的权利。</p>
    <h2>6. 试用与付费</h2>
    <p>当前价格为首发价：ESG Commitment Audit 为 US$29/月，AI Alignment Revisability Audit 为 US$99/月；各计划每月最多处理 100 个任务，并分别限前 20 个客户组织。订阅按月续费，交易与税费由 Gumroad 处理。两项公开报价均包含首次购买后 30 天无理由全额退款。取消续费后，已产生费用和依法应退款项按订单及适用消费者保护规则处理。</p>
    <h2>7. 可用性与变更</h2>
    <p>除非另签书面 SLA，本服务按“现状”和“可用”基础提供。我们会采取合理措施维护安全与连续性，但不保证服务永不中断。可能为安全、法律、维护或产品改进限制或更新功能。</p>
    <h2>8. 知识产权</h2>
    <p>开源代码适用仓库中的 Apache License 2.0；形式化材料适用其标注的 CC BY-SA 4.0。托管服务、品牌和用户文件的权利仍归各自权利人。用户保留其上传内容的权利。</p>
    <h2>9. 责任限制</h2>
    <p>在适用法律允许的最大范围内，ICS-TEC 不对因完全依赖自动分析、用户上传侵权内容或用户违反条款造成的间接损失承担责任。最终责任上限与例外将在正式条款中明确，不得排除法律禁止排除的责任。</p>
    <h2>10. 终止与联系</h2>
    <p>用户可停止使用并请求删除。严重违法、安全风险或未付款可能导致暂停或终止。联系：<a href="mailto:franka328162810@gmail.com">franka328162810@gmail.com</a>。</p>
    <nav><a href="/">返回首页</a><a href="/privacy">隐私政策草案</a></nav>
  </article>`,
);

export const activationPage = page(
  "Activate API access | ICS-TEC",
  `<article>
    <p class="eyebrow">ICS-TEC / PRODUCT ACTIVATION</p>
    <h1>Activate your API access</h1>
    <p>Enter the Gumroad license key from your purchase receipt and the organization name you want to use.</p>
    <p class="notice"><strong>Important:</strong> your ICS API key is displayed only once. Store it in a password manager and never publish it.</p>
    <form id="activation-form">
      <p>
        <label for="license-key">Gumroad license key</label><br>
        <input id="license-key" name="license_key" autocomplete="off" required maxlength="200" style="width:100%;box-sizing:border-box;padding:12px;margin-top:6px">
      </p>
      <p>
        <label for="organization-name">Organization name</label><br>
        <input id="organization-name" name="organization_name" required maxlength="160" style="width:100%;box-sizing:border-box;padding:12px;margin-top:6px">
      </p>
      <button id="activate-button" type="submit" style="padding:12px 20px;border:0;border-radius:8px;background:#0f766e;color:#fff;font-weight:700;cursor:pointer">Activate API key</button>
    </form>
    <div id="result" aria-live="polite" style="margin-top:24px"></div>
    <noscript><p class="notice">JavaScript is required for secure activation.</p></noscript>
    <nav><a href="/">Return to ESG Commitment Audit</a><a href="/terms">Terms</a><a href="/privacy">Privacy</a></nav>
  </article>
  <script>
    const form = document.getElementById("activation-form");
    const result = document.getElementById("result");
    const button = document.getElementById("activate-button");
    const product = location.pathname === "/ai-revisability-audit/activate" ? "ai" : "esg";
    function escapeHtml(value) {
      return String(value).replace(/[&<>"']/g, (character) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
      })[character]);
    }
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      result.innerHTML = "";
      button.disabled = true;
      button.textContent = "Verifying...";
      try {
        const response = await fetch("/v1/billing/gumroad/redeem", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            license_key: document.getElementById("license-key").value.trim(),
            organization_name: document.getElementById("organization-name").value.trim(),
            product
          })
        });
        const payload = await response.json();
        if (!response.ok) throw new Error(payload.error || "Activation failed");
        result.innerHTML = '<div class="notice"><strong>Activation complete.</strong><p>Copy this API key now. It will not be shown again.</p><pre style="white-space:pre-wrap;word-break:break-all;background:#102a43;color:#fff;padding:16px;border-radius:8px">' + escapeHtml(payload.api_key) + '</pre><p>Plan: ' + escapeHtml(payload.plan) + '<br>Monthly limit: ' + escapeHtml(payload.monthly_document_limit) + ' documents</p></div>';
      } catch (error) {
        result.innerHTML = '<div class="notice"><strong>Could not activate.</strong><p>' + escapeHtml(error.message) + '</p></div>';
      } finally {
        button.disabled = false;
        button.textContent = "Activate API key";
      }
    });
  </script>`,
  "en",
);

export function htmlResponse(
  body: string,
  status = 200,
  options: { allowInlineScript?: boolean } = {},
): Response {
  const scriptPolicy = options.allowInlineScript ? "'unsafe-inline'" : "'none'";
  return new Response(body, {
    status,
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "public, max-age=300",
      "x-content-type-options": "nosniff",
      "referrer-policy": "no-referrer",
      "content-security-policy":
        `default-src 'none'; style-src 'unsafe-inline'; script-src ${scriptPolicy}; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'`,
    },
  });
}
