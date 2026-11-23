import assert from "node:assert/strict";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { callTool, handleMessage } from "./server.mjs";

const originalFetch = globalThis.fetch;

function setProduct(product) {
  process.env.ICS_PRODUCT = product;
  process.env.ICS_AUDIT_API_KEY = "test_live_key";
}

function jsonResponse(payload, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "content-type": "application/json" },
  });
}

test.afterEach(() => {
  globalThis.fetch = originalFetch;
  delete process.env.ICS_PRODUCT;
  delete process.env.ICS_AUDIT_API_KEY;
  delete process.env.ICS_AUDIT_API_URL;
});

test("core initializes at version 0.5.0", async () => {
  setProduct("esg");
  const response = await handleMessage({
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: { protocolVersion: "2025-06-18" },
  });
  assert.equal(response.result.serverInfo.name, "esg-commitment-audit");
  assert.equal(response.result.serverInfo.version, "0.5.0");
});

test("ESG and AI products expose distinct tool schemas", async () => {
  setProduct("esg");
  const esgResponse = await handleMessage({
    jsonrpc: "2.0",
    id: 2,
    method: "tools/list",
  });
  const esgNames = new Set(
    esgResponse.result.tools.map((tool) => tool.name),
  );
  assert.equal(esgNames.has("audit_evidence_pack"), false);

  setProduct("ai");
  const aiResponse = await handleMessage({
    jsonrpc: "2.0",
    id: 3,
    method: "tools/list",
  });
  const aiNames = new Set(aiResponse.result.tools.map((tool) => tool.name));
  assert.equal(aiNames.has("audit_evidence_pack"), true);
  const documentTool = aiResponse.result.tools.find(
    (tool) => tool.name === "audit_document",
  );
  assert.equal(documentTool.inputSchema.properties.mode, undefined);
  assert.equal(
    documentTool.inputSchema.properties.profile.enum.includes("insurance"),
    true,
  );
});

test("missing API key produces activation guidance", async () => {
  process.env.ICS_PRODUCT = "ai";
  delete process.env.ICS_AUDIT_API_KEY;
  const response = await handleMessage({
    jsonrpc: "2.0",
    id: 4,
    method: "tools/call",
    params: { name: "get_account", arguments: {} },
  });
  assert.equal(response.result.isError, true);
  assert.match(response.result.content[0].text, /Gumroad/);
  assert.match(response.result.content[0].text, /activate/);
});

test("account response identifies plugin compatibility", async () => {
  setProduct("ai");
  globalThis.fetch = async () =>
    jsonResponse({
      plan: "ai-founding-team",
      allowed_audit_modes: ["ai-revisability", "evidence-pack"],
      remaining_documents: 100,
    });
  const account = await callTool("get_account");
  assert.equal(account.plugin_product, "ai");
  assert.equal(account.compatible, true);
  assert.deepEqual(account.expected_modes, ["ai-revisability"]);
});

test("wrong plan is rejected before an upload", async () => {
  setProduct("ai");
  let calls = 0;
  globalThis.fetch = async () => {
    calls += 1;
    return jsonResponse({
      plan: "founding-team",
      allowed_audit_modes: ["commitment", "recursive-freedom"],
    });
  };
  await assert.rejects(
    () => callTool("audit_text", { text: "AI policy", profile: "general" }),
    /cannot run 'ai-revisability'/,
  );
  assert.equal(calls, 1);
});

test("AI text audit performs account preflight and job submission", async () => {
  setProduct("ai");
  const requests = [];
  globalThis.fetch = async (url, options) => {
    requests.push({ url: String(url), method: options.method });
    if (String(url).endsWith("/v1/account")) {
      return jsonResponse({
        plan: "ai-founding-team",
        allowed_audit_modes: ["ai-revisability", "evidence-pack"],
      });
    }
    return jsonResponse(
      {
        id: "job_test",
        status: "queued",
        audit_mode: "ai-revisability",
      },
      202,
    );
  };
  const result = await callTool("audit_text", {
    text: "AI policy",
    filename: "policy.md",
    profile: "insurance",
  });
  assert.equal(result.id, "job_test");
  assert.equal(result.plugin_product, "ai");
  assert.equal(requests.length, 2);
  assert.equal(requests[0].method, "GET");
  assert.equal(requests[1].method, "POST");
});

test("AI evidence-pack tool validates ZIP and uses evidence-pack mode", async () => {
  setProduct("ai");
  const directory = await mkdtemp(path.join(os.tmpdir(), "ics-plugin-"));
  const zipPath = path.join(directory, "evidence.zip");
  await writeFile(
    zipPath,
    Buffer.from([0x50, 0x4b, 0x05, 0x06, 0, 0, 0, 0]),
  );
  let uploadedMode = "";
  globalThis.fetch = async (url, options) => {
    if (String(url).endsWith("/v1/account")) {
      return jsonResponse({
        plan: "ai-founding-team",
        allowed_audit_modes: ["ai-revisability", "evidence-pack"],
      });
    }
    uploadedMode = options.headers["X-ESG-Mode"];
    return jsonResponse({ id: "job_zip", status: "queued" }, 202);
  };
  try {
    const result = await callTool("audit_evidence_pack", { path: zipPath });
    assert.equal(result.id, "job_zip");
    assert.equal(uploadedMode, "evidence-pack");
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});
