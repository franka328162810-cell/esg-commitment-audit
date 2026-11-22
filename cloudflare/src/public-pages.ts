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
  "ICS Commitment Audit | Evidence workbench",
  `<article>
    <p class="eyebrow">ICS-TEC / ICS STUDIES</p>
    <h1>Audit the wording before you rely on the promise.</h1>
    <p>ICS Commitment Audit turns long ESG and climate reports into traceable commitment evidence. Recursive Freedom Audit for AI applies the same evidence discipline to AI rules, governance documents, and revision paths.</p>
    <div class="actions">
      <a class="button" href="https://icsstudies.gumroad.com/l/ics-commitment-audit" rel="noopener">Subscribe on Gumroad — US$29/month</a>
      <a class="button secondary" href="/workspace">Open the workbench</a>
    </div>
    <p class="notice"><strong>Evidence, not certification.</strong> This service analyses document structure. It is not audit assurance, legal advice, compliance certification, investment advice, or proof of greenwashing.</p>
    <h2>One workbench, two evidence modes</h2>
    <div class="grid">
      <div class="card">
        <h3>ESG / Climate commitments</h3>
        <p>Extract commitments with page or paragraph evidence, then test observability, enforceability, and revisability.</p>
      </div>
      <div class="card">
        <h3>Recursive Freedom Audit for AI · Beta</h3>
        <p>Check whether an AI policy states scope, ownership, review cadence, revision authority, notice, appeal, exit, monitoring, rollback, and independent oversight.</p>
        <p><a href="/recursive-freedom">Read the product scope and validation record</a></p>
      </div>
    </div>
    <h2>Founding plan</h2>
    <ul>
      <li>US$29 per month, capped at 100 audited documents per month.</li>
      <li>Up to 100 pages and 50 MB per document.</li>
      <li>Both modes are included and each completed job uses one document from the same monthly quota.</li>
      <li>TXT, Markdown, DOCX, and text-layer PDF input.</li>
      <li>Raw uploads are deleted after success or final failure; reports are retained for seven days by default.</li>
      <li>The public offer is limited to 20 Founding customers.</li>
      <li>30-day no-questions-asked full refund.</li>
    </ul>
    <h2>How to start</h2>
    <ol>
      <li>Subscribe on Gumroad and keep the license key from the receipt.</li>
      <li><a href="/activate">Activate the license</a> to receive a one-time API key.</li>
      <li>Paste the API key into the <a href="/workspace">workbench</a>, choose a mode, and upload a document.</li>
    </ol>
    <p class="notice"><strong>Beta boundary.</strong> The AI policy mode audits written governance structure only. It does not assess the personality or rights of an individual and must not be used for employment, education, credit, immigration, insurance, political, or judicial decisions.</p>
    <p class="muted">Theory source for the revision-oriented framing:
      <a href="https://doi.org/10.5281/zenodo.24217876" rel="noopener">Xue, Z. (2026), <em>On Recursive Freedom: A Theory of the Freedom to Revise</em>, DOI 10.5281/zenodo.24217876</a>.
      The software applies this idea only to documented policy structure, not to the freedom or conduct of any individual.</p>
    <h2>Developer interface</h2>
    <p>Health endpoint: <a href="/v1/health">/v1/health</a>. Source code and rules:
      <a href="https://github.com/franka328162810-cell/ics-commitment-audit">GitHub</a>.</p>
    <nav>
      <a href="/workspace">Workbench</a>
      <a href="/privacy">Privacy draft</a>
      <a href="/terms">Terms draft</a>
      <a href="mailto:franka328162810@gmail.com">Support</a>
    </nav>
    <p class="muted">Operator: Xue Zhi Xin (ICS-TEC). Last updated: 2026-11-22.</p>
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
      <a class="button secondary" href="https://icsstudies.gumroad.com/l/ics-commitment-audit" rel="noopener">Access the Founding plan</a>
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
    <p>The audit is currently included as a Beta mode in the existing US$29/month Founding plan. It shares the plan's 100-document monthly allowance and 100-page, 50 MB per-document limits. It does not yet have a separate subscription, public commitment database, or formal Codex plugin package.</p>
    <p>Planned layers are separate products rather than duplicate names:</p>
    <ul>
      <li><strong>Recursive Freedom Audit for AI:</strong> the policy-text audit described on this page.</li>
      <li><strong>AI Public Commitment & Revision Monitor:</strong> a future independent data product that tracks public policy changes over time.</li>
      <li><strong>Organizational Revisability Audit:</strong> a future professional service that tests actual governance, appeals, exit paths, and continuity, not only text.</li>
    </ul>

    <h2>Theory source</h2>
    <p>The revision-oriented framing is informed by <a href="https://doi.org/10.5281/zenodo.24217876" rel="noopener">Xue, Z. (2026), <em>On Recursive Freedom: A Theory of the Freedom to Revise</em></a>. The publication identifies intellectual provenance. It is not evidence that this rule engine has been independently validated.</p>
    <nav>
      <a href="/">Home</a>
      <a href="/workspace">Workbench</a>
      <a href="https://github.com/franka328162810-cell/ics-commitment-audit/blob/main/docs/METHODOLOGY.md" rel="noopener">Methodology</a>
      <a href="mailto:franka328162810@gmail.com">Support</a>
    </nav>
  </article>`,
  "en",
);

export const workspacePage = page(
  "Evidence Workbench | ICS Commitment Audit",
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
          <input id="api-key" type="password" autocomplete="off" spellcheck="false" placeholder="ics_live_..." required>
          <button id="connect-button" class="button" type="submit">Connect</button>
        </div>
        <p class="muted">Need a key? <a href="/activate">Activate your Gumroad license</a> or subscribe on <a href="https://icsstudies.gumroad.com/l/ics-commitment-audit" rel="noopener">Gumroad</a>.</p>
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
          <input type="radio" name="audit-mode" value="recursive-freedom">
          <strong>Recursive Freedom Audit for AI · Beta</strong>
          <span class="muted">Rules for review, revision, appeal, exit, rollback, and oversight.</span>
        </label>
      </div>
      <p id="mode-note" class="muted"></p>
      <p class="muted"><a href="/recursive-freedom">Read the Recursive Freedom Audit product scope and validation record</a></p>
      <p class="muted">The Beta's revision-oriented framing is informed by
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
    </section>

    <section aria-labelledby="upload-heading">
      <h2 id="upload-heading">3. Upload a document</h2>
      <div id="dropzone" class="dropzone" role="button" tabindex="0" aria-controls="file-input">
        <strong>Drop a file here or click to choose</strong>
        <p class="muted">PDF with a text layer, DOCX, TXT, or Markdown · maximum 50 MB · maximum 100 pages</p>
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
    const STORAGE_KEY = "ics_commitment_audit_api_key";
    const MAX_BYTES = 50 * 1024 * 1024;
    const SUPPORTED_FILE = /\\.(pdf|docx|txt|md|markdown)$/i;
    const $ = (id) => document.getElementById(id);
    const connectForm = $("connect-form");
    const apiKeyInput = $("api-key");
    const connectButton = $("connect-button");
    const connectedRow = $("connected-row");
    const accountMessage = $("account-message");
    const accountSummary = $("account-summary");
    const selectedFileLabel = $("selected-file");
    const fileInput = $("file-input");
    const dropzone = $("dropzone");
    const runButton = $("run-button");
    const runStatus = $("run-status");
    const errorBox = $("error-box");
    const reportSection = $("report-section");
    const reportContent = $("report-content");
    const cancelCurrent = $("cancel-current");
    const weightField = $("weight-field");
    const modeNote = $("mode-note");
    let apiKey = sessionStorage.getItem(STORAGE_KEY) || "";
    let selectedFile = null;
    let currentJobId = null;
    let currentReport = null;
    let pollGeneration = 0;

    function escapeHtml(value) {
      return String(value == null ? "" : value).replace(/[&<>"']/g, (character) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
      })[character]);
    }

    function selectedMode() {
      return document.querySelector('input[name="audit-mode"]:checked').value;
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
      if (showMessage) setMessage(accountMessage, "API key removed from this tab.", false);
    }

    async function connectWithKey(candidate) {
      const key = String(candidate || "").trim();
      if (!key.startsWith("ics_live_")) {
        setMessage(accountMessage, "Enter a valid ICS API key beginning with ics_live_.", true);
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
      if (!SUPPORTED_FILE.test(file.name)) {
        showError("Choose a PDF, DOCX, TXT, or Markdown file.");
        return;
      }
      if (file.size > MAX_BYTES) {
        showError("The file exceeds the 50 MB limit.");
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
      const governance = selectedMode() === "recursive-freedom";
      weightField.hidden = governance;
      modeNote.textContent = governance
        ? "Beta mode checks ten written governance controls. It analyses the policy, not an individual person or an AI system's actual behaviour."
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
      return '<div class="card"><p class="eyebrow">' +
        escapeHtml(report.report_type === "recursive-freedom" ? "Recursive Freedom Audit for AI Beta" : "ESG / Climate Commitment Audit") +
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
            "X-ICS-Filename": encodeURIComponent(selectedFile.name),
            "X-ICS-Weights": mode === "commitment" ? $("weights").value : "default",
            "X-ICS-Mode": mode
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
      if (currentReport.report_type === "recursive-freedom") {
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
  "隐私政策草案 | ICS Commitment Audit",
  `<article>
    <p class="eyebrow">隐私政策草案</p>
    <h1>我们如何处理数据</h1>
    <p class="notice"><strong>草案提示：</strong>本页是正式收费前的透明说明草案，不构成法律意见，正式商业运营前应由合格律师按实际经营主体、地区与支付方案复核。</p>
    <h2>1. 运营者与联系</h2>
    <p>运营者：Xue Zhi Xin (ICS-TEC)。隐私与删除请求：<a href="mailto:franka328162810@gmail.com">franka328162810@gmail.com</a>。</p>
    <h2>2. 处理的数据</h2>
    <ul>
      <li>用户上传的 TXT、Markdown、DOCX、PDF，以及文件名、大小和内容类型。</li>
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
    <p>当前基础设施使用 Cloudflare（Workers、D1、R2、Queues、Containers）并在其全球网络中处理数据。启用在线支付后，将使用支付服务商处理交易与账单。正式上线时会列明服务商及必要的跨境安排。</p>
    <h2>6. 安全与控制</h2>
    <p>服务采用 HTTPS、租户隔离、API Key 哈希、私有对象存储、短期报告访问和用量限制。互联网服务不存在绝对安全，用户应保护 API Key，不上传无权处理的机密或高度敏感个人信息。</p>
    <h2>7. 用户权利</h2>
    <p>用户可请求访问、更正、导出或删除与其账户有关的个人数据，并可提出投诉。请使用账户关联邮箱发送请求；为防止冒用，我们可能要求合理验证。</p>
    <h2>8. 儿童与年龄</h2>
    <p>本服务面向机构和成年专业用户，不面向未成年人，也不得用于上传未成年人的敏感个人信息。</p>
    <h2>9. 更新</h2>
    <p>重大变更将通过服务页面或账户联系渠道提示。收费正式启用前，本草案将被替换为经审查的正式版本。</p>
    <nav><a href="/">返回首页</a><a href="/terms">服务条款草案</a></nav>
  </article>`,
);

export const termsPage = page(
  "服务条款草案 | ICS Commitment Audit",
  `<article>
    <p class="eyebrow">服务条款草案</p>
    <h1>使用本服务前请阅读</h1>
    <p class="notice"><strong>草案提示：</strong>本页不构成法律意见。正式收费、订阅、退款和责任条款须在经营主体与支付方案确定后由合格律师复核。</p>
    <h2>1. 服务范围</h2>
    <p>ICS Commitment Audit 对用户提交的承诺文本做结构化抽取、评分和证据定位。结果可能不完整或存在误判，必须由用户结合原文复核。</p>
    <h2>2. 不提供专业鉴证</h2>
    <p>本服务不是审计、鉴证、法律、税务、投资或合规认证服务，不构成对“漂绿”、违法或重大性的事实认定。用户不得把结果作为唯一决策依据，也不得对外声称获得 ICS-TEC 或第三方的认证。</p>
    <h2>3. 账户与 API Key</h2>
    <p>用户应提供真实、必要的账户信息，妥善保管 API Key，并对该凭据下发生的活动负责。发现泄露应立即停用并联系我们。一个组织的额度和报告不得用于规避租户限制。</p>
    <h2>4. 上传内容与授权</h2>
    <p>用户声明其拥有处理上传内容所需的权利和合法基础。不得上传违法内容、无权披露的商业秘密、支付凭证、身份证件、医疗记录或其他与承诺分析无关的高度敏感个人信息。用户授予的服务处理许可仅限于完成请求、安全和依法履约所必需的范围。</p>
    <h2>5. 可接受使用</h2>
    <p>不得攻击、绕过配额、探测其他租户、传播恶意文件、自动生成误导性审计结论、侵犯知识产权或违反适用法律。我们可暂停高风险账户并保留依法报告的权利。</p>
    <h2>6. 试用与付费</h2>
    <p>试用额度、价格、计费周期、取消和退款将在购买页面或订单中明确。当前在线支付尚未启用。订阅取消后，已产生费用和依法应退款项按订单、适用消费者保护规则及正式条款处理。</p>
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
  "Activate API access | ICS Commitment Audit",
  `<article>
    <p class="eyebrow">ICS Commitment Audit</p>
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
    <nav><a href="/">Return to ICS Commitment Audit</a><a href="/terms">Terms</a><a href="/privacy">Privacy</a></nav>
  </article>
  <script>
    const form = document.getElementById("activation-form");
    const result = document.getElementById("result");
    const button = document.getElementById("activate-button");
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
            organization_name: document.getElementById("organization-name").value.trim()
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
