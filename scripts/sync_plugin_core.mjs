import { copyFile, mkdir } from "node:fs/promises";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const source = path.join(root, "plugins", "core", "server.mjs");
const destinations = [
  path.join(root, "plugins", "esg-commitment-audit", "server.mjs"),
  path.join(
    root,
    "plugins",
    "ai-alignment-revisability-audit",
    "server.mjs",
  ),
];

for (const destination of destinations) {
  await mkdir(path.dirname(destination), { recursive: true });
  await copyFile(source, destination);
  console.log(path.relative(root, destination));
}
