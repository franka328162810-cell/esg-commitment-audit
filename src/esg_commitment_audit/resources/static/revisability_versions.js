const versionForm = document.querySelector("#version-form");
const previousFile = document.querySelector("#previous-file");
const currentFile = document.querySelector("#current-file");
const previousName = document.querySelector("#previous-name");
const currentName = document.querySelector("#current-name");
const profile = document.querySelector("#profile");
const statusLine = document.querySelector("#status-line");
const errorPanel = document.querySelector("#error-panel");
const results = document.querySelector("#results");
const summary = document.querySelector("#summary");
const warnings = document.querySelector("#warnings");
const materialChanges = document.querySelector("#material-changes");
const statementChanges = document.querySelector("#statement-changes");
const disclaimer = document.querySelector("#disclaimer");

let lastPayload = null;

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = String(text);
  return node;
}

function sourceLabel(evidence) {
  if (!evidence) return "—";
  const page = evidence.page_number ? `p.${evidence.page_number}, ` : "";
  return `${page}paragraph ${evidence.paragraph_index}`;
}

function gradePill(value, className) {
  return el("span", className, value);
}

function table(headers, rows) {
  const node = el("table", "version-table");
  const thead = el("thead");
  const headerRow = el("tr");
  headers.forEach((header) => headerRow.append(el("th", "", header)));
  thead.append(headerRow);
  node.append(thead);
  const tbody = el("tbody");
  if (!rows.length) {
    const row = el("tr");
    const cell = el("td", "", "没有发现这一类变化。");
    cell.colSpan = headers.length;
    row.append(cell);
    tbody.append(row);
  } else {
    rows.forEach((values) => {
      const row = el("tr");
      values.forEach((value) => {
        const cell = el("td");
        if (value instanceof Node) cell.append(value);
        else cell.textContent = value === undefined || value === null ? "" : String(value);
        row.append(cell);
      });
      tbody.append(row);
    });
  }
  node.append(tbody);
  return node;
}

function renderReport(report) {
  summary.replaceChildren();
  warnings.replaceChildren();
  materialChanges.replaceChildren();
  statementChanges.replaceChildren();
  disclaimer.textContent = report.disclaimer;

  const cards = [
    [report.summary.improved_count, "检查等级提升"],
    [report.summary.regressed_count, "检查等级下降"],
    [report.summary.high_materiality_count, "高重要性下降"],
    [report.summary.added_statement_count, "新增条款"],
    [report.summary.removed_statement_count, "删除条款"],
    [report.summary.modified_statement_count, "修改条款"],
  ];
  cards.forEach(([value, label]) => {
    const card = el("article", "summary-card");
    card.append(el("strong", "", value), el("span", "", label));
    summary.append(card);
  });

  report.new_warnings.forEach((item) => warnings.append(el("p", "notice", `New warning: ${item}`)));
  report.resolved_warnings.forEach((item) => warnings.append(el("p", "", `Resolved warning: ${item}`)));

  materialChanges.append(el("h3", "", "检查等级变化"));
  materialChanges.append(
    table(
      ["Check", "Previous", "Current", "Direction", "Materiality"],
      report.material_changes.map((change) => [
        change.label,
        change.previous_grade,
        change.current_grade,
        gradePill(change.direction, `status-pill direction-${change.direction}`),
        gradePill(change.materiality, `status-pill materiality-${change.materiality}`),
      ]),
    ),
  );

  statementChanges.append(el("h3", "", "具体条款变化"));
  statementChanges.append(
    table(
      ["Type", "Similarity", "Previous source", "Current source", "Text"],
      report.statement_changes.map((change) => {
        let text = "";
        if (change.change_type === "added") {
          text = change.current?.excerpt || "";
        } else if (change.change_type === "removed") {
          text = change.previous?.excerpt || "";
        } else {
          text = `Previous: ${change.previous?.excerpt || ""} | Current: ${change.current?.excerpt || ""}`;
        }
        return [
          gradePill(change.change_type, `status-pill direction-${change.change_type === "added" ? "improved" : change.change_type === "removed" ? "regressed" : "changed"}`),
          change.similarity === null ? "—" : change.similarity.toFixed(2),
          sourceLabel(change.previous),
          sourceLabel(change.current),
          text,
        ];
      }),
    ),
  );

  results.hidden = false;
  results.scrollIntoView({ behavior: "smooth", block: "start" });
}

previousFile.addEventListener("change", () => {
  previousName.textContent = previousFile.files[0]?.name || "尚未选择文件";
});
currentFile.addEventListener("change", () => {
  currentName.textContent = currentFile.files[0]?.name || "尚未选择文件";
});

versionForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!previousFile.files[0] || !currentFile.files[0]) {
    errorPanel.textContent = "请选择旧版和新版两个文件。";
    errorPanel.hidden = false;
    return;
  }
  const data = new FormData();
  data.append("previous_file", previousFile.files[0]);
  data.append("current_file", currentFile.files[0]);
  data.append("profile", profile.value);
  document.querySelectorAll("button[type='submit']").forEach((button) => {
    button.disabled = true;
  });
  statusLine.textContent = "正在比较两个版本…";
  errorPanel.hidden = true;
  try {
    const response = await fetch("/api/revisability-version", {
      method: "POST",
      body: data,
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || `Request failed with status ${response.status}`);
    lastPayload = payload;
    renderReport(payload.report);
    statusLine.textContent = "版本比较完成。";
  } catch (error) {
    errorPanel.textContent = error.message || "版本比较失败。";
    errorPanel.hidden = false;
    statusLine.textContent = "";
  } finally {
    document.querySelectorAll("button[type='submit']").forEach((button) => {
      button.disabled = false;
    });
  }
});

function download(content, filename, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

document.querySelector("#download-html").addEventListener("click", () => {
  if (lastPayload) download(lastPayload.html, "ai-revisability-version-trace.html", "text/html;charset=utf-8");
});
document.querySelector("#download-markdown").addEventListener("click", () => {
  if (lastPayload) download(lastPayload.markdown, "ai-revisability-version-trace.md", "text/markdown;charset=utf-8");
});
document.querySelector("#download-json").addEventListener("click", () => {
  if (lastPayload) download(JSON.stringify(lastPayload.report, null, 2), "ai-revisability-version-trace.json", "application/json;charset=utf-8");
});
