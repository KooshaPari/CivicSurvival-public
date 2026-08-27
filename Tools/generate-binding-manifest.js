#!/usr/bin/env node
/* Public-snapshot read-only binding manifest check. Licensed generators stay external. */
const fs = require("fs");
const path = require("path");

const root = path.resolve(
  process.env.CIVIC_REPO_ROOT || path.join(__dirname, ".."),
);
const sourcePaths = [
  "CivicSurvival/Core/UI/BindingNames.cs",
  "CivicSurvival/Core/UI/BindingNames.Dto.g.cs",
  "CivicSurvival/Core/UI/BindingNames.Trigger.g.cs",
].map((relative) => path.join(root, relative));
const generatedPath = path.join(
  root,
  "CivicSurvival/UI/src/hooks/bindingNames.generated.ts",
);
const source = sourcePaths
  .map((file) => fs.readFileSync(file, "utf8"))
  .join("\n");
const generated = fs.readFileSync(generatedPath, "utf8");
const sourceEntries = [
  ...source.matchAll(/public\s+const\s+string\s+(\w+)\s*=\s*"([^"]+)"/g),
].map((m) => [m[1], m[2]]);
const sourceMap = new Map(sourceEntries);
const object = generated.match(/export const B = \{([\s\S]*?)\n\} as const;/);
if (!object) {
  console.error("binding manifest check failed; generated B object is missing");
  process.exit(1);
}
const generatedMap = new Map(
  [...object[1].matchAll(/^\s+(\w+)\s*:\s*"([^"]+)"\s*,?$/gm)].map((m) => [
    m[1],
    m[2],
  ]),
);
const missing = [...sourceMap.keys()].filter((key) => !generatedMap.has(key));
const unexpected = [...generatedMap.keys()].filter(
  (key) => !sourceMap.has(key),
);
const mismatched = [...sourceMap.keys()].filter(
  (key) =>
    generatedMap.has(key) && generatedMap.get(key) !== sourceMap.get(key),
);
if (
  missing.length ||
  unexpected.length ||
  mismatched.length ||
  generatedMap.size !== sourceMap.size
) {
  console.error(
    `binding manifest check failed; missing: ${missing.join(", ") || "none"}; unexpected: ${unexpected.join(", ") || "none"}; mismatched: ${mismatched.join(", ") || "none"}`,
  );
  process.exit(1);
}
console.log(`binding manifest check passed: ${sourceMap.size} values`);
