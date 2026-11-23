import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import path from "node:path";
import test from "node:test";

const root = path.resolve(import.meta.dirname, "..", "..");

async function json(relativePath) {
  return JSON.parse(await readFile(path.join(root, relativePath), "utf8"));
}

test("marketplace exposes exactly two independent ICS plugins", async () => {
  const marketplace = await json(".agents/plugins/marketplace.json");
  assert.equal(marketplace.name, "ics-tec");
  assert.deepEqual(
    marketplace.plugins.map((plugin) => plugin.name).sort(),
    ["ai-alignment-revisability-audit", "esg-commitment-audit"],
  );
  assert.deepEqual(
    marketplace.plugins.map((plugin) => plugin.source.path).sort(),
    [
      "./plugins/ai-alignment-revisability-audit",
      "./plugins/esg-commitment-audit",
    ],
  );
});

test("both plugin bundles use the same 0.6.0 MCP core", async () => {
  const canonical = await readFile(
    path.join(root, "plugins", "core", "server.mjs"),
  );
  const canonicalHash = createHash("sha256").update(canonical).digest("hex");
  for (const name of [
    "esg-commitment-audit",
    "ai-alignment-revisability-audit",
  ]) {
    const bundled = await readFile(
      path.join(root, "plugins", name, "server.mjs"),
    );
    assert.equal(
      createHash("sha256").update(bundled).digest("hex"),
      canonicalHash,
    );
  }
});

test("plugin manifests and MCP permissions are product-specific", async () => {
  const esgManifest = await json(
    "plugins/esg-commitment-audit/.codex-plugin/plugin.json",
  );
  const aiManifest = await json(
    "plugins/ai-alignment-revisability-audit/.codex-plugin/plugin.json",
  );
  assert.equal(esgManifest.version, "0.6.0");
  assert.equal(aiManifest.version, "0.6.0");
  assert.equal(esgManifest.name, "esg-commitment-audit");
  assert.equal(aiManifest.name, "ai-alignment-revisability-audit");
  assert.deepEqual(esgManifest.interface.capabilities, ["Read", "Write"]);
  assert.deepEqual(aiManifest.interface.capabilities, ["Read", "Write"]);

  const esgMcp = await json("plugins/esg-commitment-audit/.mcp.json");
  const aiMcp = await json(
    "plugins/ai-alignment-revisability-audit/.mcp.json",
  );
  const esgServer = esgMcp.mcpServers["esg-commitment-audit"];
  const aiServer = aiMcp.mcpServers["ai-alignment-revisability-audit"];
  assert.equal(esgServer.env.ICS_PRODUCT, "esg");
  assert.equal(aiServer.env.ICS_PRODUCT, "ai");
  assert.equal(esgServer.tools.audit_document.approval_mode, "prompt");
  assert.equal(aiServer.tools.audit_document.approval_mode, "prompt");
  assert.equal(aiServer.tools.audit_evidence_pack.approval_mode, "prompt");
  assert.equal(esgServer.tools.audit_evidence_pack, undefined);
});

test("both skills are named after their plugin entries", async () => {
  for (const name of [
    "esg-commitment-audit",
    "ai-alignment-revisability-audit",
  ]) {
    const skill = await readFile(
      path.join(root, "plugins", name, "skills", name, "SKILL.md"),
      "utf8",
    );
    assert.match(skill, new RegExp(`^---\\nname: ${name}\\n`, "m"));
    assert.match(skill, /get_account/);
    assert.match(skill, /activation/);
  }
});
