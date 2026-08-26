#!/usr/bin/env node
/* Public snapshot verifies generated projections; private codegen remains host-owned. */
const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const root = path.resolve(__dirname, "..");
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
const missing = generated.filter(
  (relative) => !fs.existsSync(path.join(root, relative)),
);
if (missing.length) {
  console.error(
    `generated contract projections missing: ${missing.join(", ")}`,
  );
  process.exit(1);
}
console.log("binding codegen projection check passed");
