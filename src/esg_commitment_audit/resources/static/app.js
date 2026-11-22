const uploadForm = document.querySelector("#upload-form");
const textForm = document.querySelector("#text-form");
const fileInput = document.querySelector("#file-input");
const selectedFile = document.querySelector("#selected-file");
const textInput = document.querySelector("#text-input");
const weights = document.querySelector("#weights");
const statusLine = document.querySelector("#status-line");
const errorPanel = document.querySelector("#error-panel");
const results = document.querySelector("#results");
const summary = document.querySelector("#summary");
const documentWarnings = document.querySelector("#document-warnings");
const commitments = document.querySelector("#commitments");
const disclaimer = document.querySelector("#disclaimer");

let lastPayload = null;

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = String(text);
  return node;
}

function setBusy(isBusy, message = "") {
  document.querySelectorAll("button[type='submit']").forEach((button) => {
    button.disabled = isBusy;
  });
  statusLine.textContent = message;
  if (isBusy) {
    errorPanel.hidden = true;
  }
}

function showError(message) {
  errorPanel.textContent = message;
  errorPanel.hidden = false;
  statusLine.textContent = "";
}

function sourceLabel(evidence) {
  if (evidence.page_number) return `第 ${evidence.page_number} 页 · 第 ${evidence.paragraph_index} 段`;
  return `第 ${evidence.paragraph_index} 段`;
}

function statusClass(status) {
  return `status-pill status-${status}`;
}

const statusLabels = {
  present: "已发现",
  missing: "缺失",
  partial: "部分",
};

function renderReport(report) {
  summary.replaceChildren();
  documentWarnings.replaceChildren();
  commitments.replaceChildren();
  disclaimer.textContent = report.disclaimer;

  const cards = [
    [report.summary.commitment_count, "识别到的承诺"],
    [
      report.summary.average_crv === null ? "N/A" : report.summary.average_crv.toFixed(3),
      "平均 CRV 结构分",
    ],
    [report.summary.high_structure_count, "高结构完整性承诺"],
    [
      report.summary.limited_structure_count,
      "有限结构完整性承诺",
    ],
  ];
  for (const [value, label] of cards) {
    const card = el("article", "summary-card");
    card.append(el("strong", "", value), el("span", "", label));
    summary.append(card);
  }

  const warnings = report.summary.document_warnings || [];
  for (const warning of warnings) {
    documentWarnings.append(el("p", "notice", warning));
  }

  if (!report.commitments.length) {
    commitments.append(
      el(
        "p",
        "notice",
        "没有识别到符合当前规则的承诺。这不证明文件中不存在承诺，请检查规则覆盖或拆分原文后重试。",
      ),
    );
    return;
  }

  report.commitments.forEach((item, index) => {
    const card = el("article", "commitment-card");
    const header = el("div", "commitment-header");
    const titleBlock = el("div");
    titleBlock.append(
      el("p", "step-label", `COMMITMENT ${index + 1} · ${item.subcategory}`),
      el("h3", "", item.commitment_id),
      el("p", "commitment-text", item.evidence.excerpt),
    );
    const grade = el("div", "grade-block");
    grade.append(
      el("strong", "", item.crv_score.toFixed(3)),
      el("span", "", item.grade),
    );
    header.append(titleBlock, grade);
    card.append(header);
    card.append(
      el(
        "p",
        "source-line",
        `${sourceLabel(item.evidence)} · 抽取置信度 ${item.extraction_confidence.toFixed(2)} · 承诺强度 ${item.strength}`,
      ),
    );

    const dimensionGrid = el("div", "dimension-grid");
    item.dimensions.forEach((dimension) => {
      const dimensionNode = el("section", "dimension");
      const dimensionHead = el("div", "dimension-head");
      dimensionHead.append(
        el("h4", "", dimension.label),
        el("span", "dimension-score", dimension.score.toFixed(3)),
      );
      dimensionNode.append(dimensionHead);

      dimension.checks.forEach((check) => {
        const checkNode = el("div", "check");
        checkNode.append(
          el("span", "check-name", check.label),
          el("span", "check-points", `${check.points.toFixed(2)} / ${check.weight.toFixed(2)}`),
          el("span", statusClass(check.status), statusLabels[check.status] || check.status),
          el("span", "check-note", check.note),
        );
        dimensionNode.append(checkNode);
      });
      dimensionGrid.append(dimensionNode);
    });
    card.append(dimensionGrid);

    const lists = el("div", "card-lists");
    for (const [heading, values] of [
      ["风险提示", item.warnings],
      ["建议补充内容", item.recommendations],
    ]) {
      const section = el("section", "card-list");
      section.append(el("h4", "", heading));
      const list = el("ul");
      if (values.length) {
        values.forEach((value) => list.append(el("li", "", value)));
      } else {
        list.append(el("li", "", "当前规则未发现需要提示的项目。"));
      }
      section.append(list);
      lists.append(section);
    }
    card.append(lists);
    commitments.append(card);
  });

  results.hidden = false;
  results.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function sendRequest(url, options, busyMessage) {
  setBusy(true, busyMessage);
  try {
    const response = await fetch(url, options);
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || `Request failed with status ${response.status}`);
    }
    lastPayload = payload;
    renderReport(payload.report);
    statusLine.textContent = "审计完成。";
  } catch (error) {
    showError(error.message || "审计失败。");
  } finally {
    setBusy(false, statusLine.textContent);
  }
}

fileInput.addEventListener("change", () => {
  selectedFile.textContent = fileInput.files[0]?.name || "尚未选择文件";
});

["dragenter", "dragover"].forEach((eventName) => {
  uploadForm.addEventListener(eventName, (event) => {
    event.preventDefault();
    uploadForm.classList.add("dragging");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  uploadForm.addEventListener(eventName, (event) => {
    event.preventDefault();
    uploadForm.classList.remove("dragging");
  });
});

uploadForm.addEventListener("drop", (event) => {
  const file = event.dataTransfer.files[0];
  if (!file) return;
  const transfer = new DataTransfer();
  transfer.items.add(file);
  fileInput.files = transfer.files;
  selectedFile.textContent = file.name;
});

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = fileInput.files[0];
  if (!file) {
    showError("请先选择一个文件。");
    return;
  }
  const data = new FormData();
  data.append("file", file);
  data.append("weights", weights.value);
  await sendRequest("/api/audit", { method: "POST", body: data }, "正在解析并审计文件…");
});

textForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = textInput.value.trim();
  if (!text) {
    showError("请先粘贴要审计的文本。");
    return;
  }
  await sendRequest(
    "/api/audit-text",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        filename: "pasted-text.txt",
        weights: weights.value,
      }),
    },
    "正在审计粘贴文本…",
  );
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
  if (!lastPayload) return;
  download(lastPayload.html, "esg-commitment-audit-report.html", "text/html;charset=utf-8");
});

document.querySelector("#download-markdown").addEventListener("click", () => {
  if (!lastPayload) return;
  download(lastPayload.markdown, "esg-commitment-audit-report.md", "text/markdown;charset=utf-8");
});

document.querySelector("#download-json").addEventListener("click", () => {
  if (!lastPayload) return;
  download(
    JSON.stringify(lastPayload.report, null, 2),
    "esg-commitment-audit-report.json",
    "application/json;charset=utf-8",
  );
});
