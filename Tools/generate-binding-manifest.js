#!/usr/bin/env node
/* Public-snapshot read-only binding manifest check. Licensed generators stay external. */
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const sourcePath = path.join(root, "CivicSurvival/Core/UI/BindingNames.cs");
const generatedPath = path.join(
  root,
  "CivicSurvival/UI/src/hooks/bindingNames.generated.ts",
);
const source = fs.readFileSync(sourcePath, "utf8");
const generated = fs.readFileSync(generatedPath, "utf8");
const values = [
  ...source.matchAll(/public\s+const\s+string\s+\w+\s*=\s*"([^"]+)"/g),
].map((m) => m[1]);
const missing = [...new Set(values)].filter(
  (value) => !generated.includes(`"${value}"`),
);
if (missing.length) {
  console.error(
    `binding manifest check failed; missing: ${missing.join(", ")}`,
  );
  process.exit(1);
}
console.log(`binding manifest check passed: ${new Set(values).size} values`);
