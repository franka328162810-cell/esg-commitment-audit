import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { access, readFile } from "node:fs/promises";
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
    marketplace.plugins.map((plugin) => plugin.name),
    ["ai-alignment-revisability-audit", "esg-commitment-audit"],
  );
  assert.deepEqual(
    marketplace.plugins.map((plugin) => plugin.source.path),
    [
      "./plugins/ai-alignment-revisability-audit",
      "./plugins/esg-commitment-audit",
    ],
  );
});

test("both plugin bundles use the same 0.6.2 MCP core", async () => {
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
  assert.equal(esgManifest.version, "0.6.2");
  assert.equal(aiManifest.version, "0.6.2");
  assert.equal(esgManifest.name, "esg-commitment-audit");
  assert.equal(aiManifest.name, "ai-alignment-revisability-audit");
  assert.match(aiManifest.homepage, /\/ai-revisability-audit$/);
  assert.match(esgManifest.homepage, /workers\.dev\/$/);
  assert.deepEqual(esgManifest.interface.capabilities, ["Read", "Write"]);
  assert.deepEqual(aiManifest.interface.capabilities, ["Read", "Write"]);
  for (const [pluginRoot, manifest] of [
    ["plugins/ai-alignment-revisability-audit", aiManifest],
    ["plugins/esg-commitment-audit", esgManifest],
  ]) {
    assert.deepEqual(manifest.interface.screenshots, [
      "./assets/cover.png",
      "./assets/thumbnail.png",
    ]);
    for (const relativePath of manifest.interface.screenshots) {
      await access(path.join(root, pluginRoot, relativePath));
    }
  }

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

test("each plugin ships its own cover and thumbnail", async () => {
  const products = [
    "ai-alignment-revisability-audit",
    "esg-commitment-audit",
  ];
  const hashes = new Map();
  for (const product of products) {
    for (const asset of ["cover.png", "thumbnail.png"]) {
      const bytes = await readFile(
        path.join(root, "plugins", product, "assets", asset),
      );
      const rootAsset = `${product}-${asset === "cover.png" ? "cover" : "thumbnail"}.png`;
      const rootBytes = await readFile(
        path.join(root, "assets", rootAsset),
      );
      assert.equal(
        createHash("sha256").update(bytes).digest("hex"),
        createHash("sha256").update(rootBytes).digest("hex"),
      );
      hashes.set(
        `${product}:${asset}`,
        createHash("sha256").update(bytes).digest("hex"),
      );
    }
  }
  assert.notEqual(
    hashes.get("ai-alignment-revisability-audit:cover.png"),
    hashes.get("esg-commitment-audit:cover.png"),
  );
  assert.notEqual(
    hashes.get("ai-alignment-revisability-audit:thumbnail.png"),
    hashes.get("esg-commitment-audit:thumbnail.png"),
  );
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

test("cross-client adapters are present and secret-free", async () => {
  const adapterPaths = [
    "adapters/claude-code/.mcp.json",
    "adapters/claude-code/remote-mcp.json",
    "adapters/hermes/mcp.json",
    "adapters/workbuddy/mcp.json",
    "adapters/generic/mcp-stdio.json",
  ];
  for (const relativePath of adapterPaths) {
    const content = await readFile(path.join(root, relativePath), "utf8");
    assert.equal(/(?:ai|esg)_live_[A-Za-z0-9_-]{20,}/.test(content), false);
    JSON.parse(content);
  }
  const claude = await json("adapters/claude-code/.mcp.json");
  await access(
    path.join(
      root,
      claude.mcpServers["ics-esg-commitment-audit"].args[0],
    ),
  );
  await access(
    path.join(
      root,
      claude.mcpServers["ics-ai-alignment-revisability-audit"].args[0],
    ),
  );
  const remote = await json("adapters/claude-code/remote-mcp.json");
  assert.match(
    remote.mcpServers["ics-esg-commitment-audit-remote"].url,
    /\/mcp\/esg$/,
  );
  assert.match(
    remote.mcpServers["ics-ai-alignment-revisability-audit-remote"].url,
    /\/mcp\/ai$/,
  );
});
