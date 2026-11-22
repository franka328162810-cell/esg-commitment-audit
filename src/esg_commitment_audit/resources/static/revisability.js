const uploadForm = document.querySelector("#upload-form");
const textForm = document.querySelector("#text-form");
const fileInput = document.querySelector("#file-input");
const selectedFile = document.querySelector("#selected-file");
const textInput = document.querySelector("#text-input");
const profile = document.querySelector("#profile");
const statusLine = document.querySelector("#status-line");
const errorPanel = document.querySelector("#error-panel");
const results = document.querySelector("#results");
const summary = document.querySelector("#summary");
const warnings = document.querySelector("#warnings");
const dimensions = document.querySelector("#dimensions");
const actions = document.querySelector("#actions");
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
  if (isBusy) errorPanel.hidden = true;
}

function showError(message) {
  errorPanel.textContent = message;
  errorPanel.hidden = false;
  statusLine.textContent = "";
}

function gradeClass(grade) {
  return `grade-pill grade-${grade}`;
}

function sourceLabel(evidence) {
  if (!evidence) return "未找到支撑原文";
  const page = evidence.page_number ? `第 ${evidence.page_number} 页 · ` : "";
  return `${page}第 ${evidence.paragraph_index} 段`;
}

function renderReport(report) {
  summary.replaceChildren();
  warnings.replaceChildren();
  dimensions.replaceChildren();
  actions.replaceChildren();
  disclaimer.textContent = report.disclaimer;

  const cards = [
    [report.summary.check_count, "审查项"],
    [report.summary.documented_count, "有具体书面制度"],
    [report.summary.asserted_count, "只有原则性声称"],
    [report.summary.absent_count, "文本未发现"],
    [report.summary.contradicted_count, "出现冲突或封闭"],
  ];
  for (const [value, label] of cards) {
    const card = el("article", "summary-card");
    card.append(el("strong", "", value), el("span", "", label));
    summary.append(card);
  }

  for (const warning of report.warnings || []) {
    warnings.append(el("p", "notice", warning));
  }

  for (const dimension of report.dimensions) {
    const card = el("article", "revisability-dimension");
    const header = el("header");
    header.append(el("p", "step-label", dimension.key.toUpperCase()));
    header.append(el("h3", "", dimension.label));
    card.append(header);
    const checks = el("div", "revisability-checks");

    for (const check of dimension.checks) {
      const item = el("section", "revisability-check");
      const heading = el("div", "check-heading");
      heading.append(el("h4", "", check.label));
      heading.append(el("span", gradeClass(check.grade), check.grade.replaceAll("_", " ")));
      item.append(heading);
      item.append(el("p", "check-rationale", check.rationale));

      if (check.evidence.length) {
        const evidence = check.evidence[0];
        item.append(el("blockquote", "", evidence.excerpt));
        item.append(el("p", "check-source", sourceLabel(evidence)));
      } else {
        item.append(el("p", "check-source", "审查文本没有提供可引用的支持原文。"));
      }

      if (check.required_artifacts.length) {
        item.append(el("p", "check-rationale", "进一步证据："));
        const list = el("ul", "check-artifacts");
        check.required_artifacts.forEach((artifact) => list.append(el("li", "", artifact)));
        item.append(list);
      }
      checks.append(item);
    }
    card.append(checks);
    dimensions.append(card);
  }

  for (const [title, values] of [
    ["优先建议", report.recommendations],
    ["需要补充的证据", report.evidence_requests],
  ]) {
    const card = el("section", "action-card");
    card.append(el("h3", "", title));
    const list = el("ul");
    if (values.length) {
      values.forEach((value) => list.append(el("li", "", value)));
    } else {
      list.append(el("li", "", "当前规则未发现需要补充的项目。"));
    }
    card.append(list);
    actions.append(card);
  }

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
    statusLine.textContent = "审查完成。";
  } catch (error) {
    showError(error.message || "审查失败。");
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
  data.append("profile", profile.value);
  await sendRequest(
    "/api/revisability",
    { method: "POST", body: data },
    "正在解析并审查治理文件…",
  );
});

textForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = textInput.value.trim();
  if (!text) {
    showError("请先粘贴要审查的文本。");
    return;
  }
  await sendRequest(
    "/api/revisability-text",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        filename: "pasted-ai-policy.txt",
        profile: profile.value,
      }),
    },
    "正在审查粘贴文本…",
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
  download(lastPayload.html, "ai-alignment-revisability-audit.html", "text/html;charset=utf-8");
});

document.querySelector("#download-markdown").addEventListener("click", () => {
  if (!lastPayload) return;
  download(lastPayload.markdown, "ai-alignment-revisability-audit.md", "text/markdown;charset=utf-8");
});

document.querySelector("#download-json").addEventListener("click", () => {
  if (!lastPayload) return;
  download(
    JSON.stringify(lastPayload.report, null, 2),
    "ai-alignment-revisability-audit.json",
    "application/json;charset=utf-8",
  );
});
