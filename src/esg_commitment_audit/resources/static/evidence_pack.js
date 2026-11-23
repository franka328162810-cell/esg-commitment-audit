const form = document.querySelector("#evidence-form");
const fileInput = document.querySelector("#evidence-file");
const statusLine = document.querySelector("#status-line");
const errorPanel = document.querySelector("#error-panel");
const results = document.querySelector("#results");

let lastPayload = null;

function el(tag, className = "", text = "") {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text) node.textContent = text;
  return node;
}

function setStatus(message, busy = false) {
  statusLine.textContent = message;
  statusLine.dataset.busy = busy ? "true" : "false";
}

function showError(message) {
  errorPanel.hidden = false;
  errorPanel.textContent = message;
}

function clearError() {
  errorPanel.hidden = true;
  errorPanel.textContent = "";
}

function table(headers, rows) {
  const node = el("table", "evidence-table");
  const thead = el("thead");
  const headRow = el("tr");
  for (const header of headers) headRow.append(el("th", "", header));
  thead.append(headRow);
  const tbody = el("tbody");
  for (const row of rows) {
    const tr = el("tr");
    for (const value of row) {
      const td = el("td");
      if (value instanceof Node) td.append(value);
      else td.textContent = value ?? "—";
      tr.append(td);
    }
    tbody.append(tr);
  }
  node.append(thead, tbody);
  return node;
}

function code(value) {
  return el("span", "evidence-code", value ?? "—");
}

function codeList(values) {
  const wrapper = el("span");
  values.forEach((value, index) => {
    if (index) wrapper.append(document.createTextNode(", "));
    wrapper.append(code(value));
  });
  return wrapper;
}

function renderReport(report) {
  document.querySelector("#summary").replaceChildren(
    metric("Organization", report.organization),
    metric("Base document", report.base_document),
    metric("Promotions", report.promotions.length),
    metric("Remaining gaps", report.unresolved_controls.length),
    metric("Warnings", report.warnings.length),
  );

  const inventory = document.querySelector("#inventory-section");
  inventory.replaceChildren(el("h3", "", "Artifact inventory"));
  inventory.append(table(
    ["Artifact", "Type", "Issuer", "Issued", "Hash", "E3 eligible", "Warnings"],
    report.artifact_inventory.map((item) => [
      code(item.path),
      code(item.artifact_type),
      item.issuer,
      item.issued_at,
      item.hash_matches === true ? "matched" : item.hash_matches === false ? "mismatch" : "not pinned",
      item.eligible_for_operational_evidence ? "yes" : "no",
      item.warnings.join("; "),
    ]),
  ));

  const promotions = document.querySelector("#promotions-section");
  promotions.replaceChildren(el("h3", "", "Proposed evidence-grade promotions"));
  if (report.promotions.length) {
    promotions.append(table(
      ["Control", "Baseline", "Proposed", "Artifacts", "Human confirmation"],
      report.promotions.map((item) => [
        code(item.check_key),
        item.baseline_grade,
        item.proposed_grade,
        codeList(item.supporting_artifacts),
        item.requires_human_confirmation ? "required" : "not required",
      ]),
    ));
  } else {
    promotions.append(el("p", "subtitle", "No promotion was proposed."));
  }

  const gaps = document.querySelector("#gaps-section");
  gaps.replaceChildren(el("h3", "", "Remaining evidence gaps"));
  if (report.unresolved_controls.length) {
    gaps.append(table(
      ["Control", "Baseline", "Compatible artifact types"],
      report.unresolved_controls.map((item) => [
        code(item.check_key),
        item.baseline_grade,
        item.missing_artifact_types.join(", "),
      ]),
    ));
  } else {
    gaps.append(el("p", "subtitle", "No mapped gap remains."));
  }

  const warnings = document.querySelector("#warnings-section");
  warnings.replaceChildren();
  if (report.warnings.length) {
    warnings.append(el("h3", "", "Warnings"));
    const list = el("ul");
    for (const warning of report.warnings) list.append(el("li", "", warning));
    warnings.append(list);
  }
  document.querySelector("#disclaimer").textContent = report.disclaimer;
  results.hidden = false;
}

function metric(label, value) {
  const box = el("article", "summary-card");
  box.append(el("span", "", label), el("strong", "", String(value)));
  return box;
}

function download(content, filename, type) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const link = el("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearError();
  results.hidden = true;
  if (!fileInput.files.length) return;

  const body = new FormData();
  body.append("file", fileInput.files[0]);
  setStatus("正在校验哈希和控制项映射……", true);
  try {
    const response = await fetch("/api/evidence-pack", { method: "POST", body });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "证据包校验失败");
    lastPayload = payload;
    renderReport(payload.report);
    setStatus("证据包校验完成。E3/E4 仍须人工确认。");
  } catch (error) {
    showError(error.message);
    setStatus("证据包未生成报告。");
  }
});

document.querySelector("#download-html").addEventListener("click", () => {
  if (lastPayload) download(lastPayload.html, "ai-revisability-evidence-pack.html", "text/html;charset=utf-8");
});

document.querySelector("#download-markdown").addEventListener("click", () => {
  if (lastPayload) download(lastPayload.markdown, "ai-revisability-evidence-pack.md", "text/markdown;charset=utf-8");
});

document.querySelector("#download-json").addEventListener("click", () => {
  if (lastPayload) {
    download(JSON.stringify(lastPayload.report, null, 2), "ai-revisability-evidence-pack.json", "application/json;charset=utf-8");
  }
});
