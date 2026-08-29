#!/usr/bin/env node
/* Public snapshot verifies generated projections; private codegen remains host-owned. */
const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const root = path.resolve(
  process.env.CIVIC_REPO_ROOT || path.join(__dirname, ".."),
);
const check = spawnSync(
  process.execPath,
  [path.join(__dirname, "generate-binding-manifest.js"), "--check"],
  { encoding: "utf8" },
);
if (check.status !== 0) {
  process.stderr.write(check.stderr || check.stdout);
  process.exit(check.status || 1);
}
const generated = [
  "CivicSurvival/UI/src/hooks/bindingNames.generated.ts",
  "CivicSurvival/UI/src/hooks/typedBinding.generated.ts",
  "CivicSurvival/UI/src/types/triggerSignatures.generated.ts",
];
const missing = generated.filter((relative) => {
  const file = path.join(root, relative);
  return !fs.existsSync(file) || fs.statSync(file).size === 0;
});
if (missing.length) {
  console.error(
    `generated contract projections missing or empty: ${missing.join(", ")}`,
  );
  process.exit(1);
}
const typed = fs.readFileSync(path.join(root, generated[1]), "utf8");
const triggers = fs.readFileSync(path.join(root, generated[2]), "utf8");
if (
  !typed.includes("export function bindCivicValue") ||
  !triggers.includes("interface TriggerArgRegistry")
) {
  console.error("generated contract projections have unexpected structure");
  process.exit(1);
}
console.log("binding codegen projection check passed");
