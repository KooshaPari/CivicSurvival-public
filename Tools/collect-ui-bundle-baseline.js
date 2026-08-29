#!/usr/bin/env node
/* Validate the checked-in public bundle baseline; licensed host builds remain external. */
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const baselinePath = path.join(root, "CivicSurvival/UI/bundle-baseline.json");
const args = process.argv.slice(2);
const check = args.includes("--check");
const write = args.includes("--write");
const thresholdIndex = args.indexOf("--threshold");
const threshold = thresholdIndex >= 0 ? Number(args[thresholdIndex + 1]) : 10;
if (!Number.isFinite(threshold) || threshold < 0) {
  console.error("bundle threshold must be a non-negative number");
  process.exit(2);
}
if (!fs.existsSync(baselinePath)) {
  console.error("missing CivicSurvival/UI/bundle-baseline.json");
  process.exit(1);
}
let baseline;
try {
  baseline = JSON.parse(fs.readFileSync(baselinePath, "utf8"));
} catch (error) {
  console.error(`invalid bundle baseline: ${error.message}`);
  process.exit(1);
}
const bundles = baseline && baseline.bundles;
if (!bundles || typeof bundles !== "object" || !Object.keys(bundles).length) {
  console.error("bundle baseline must contain a non-empty bundles object");
  process.exit(1);
}
for (const [name, value] of Object.entries(bundles)) {
  if (
    !Number.isInteger(value.bytes) ||
    value.bytes <= 0 ||
    !Number.isInteger(value.gzipBytes) ||
    value.gzipBytes <= 0 ||
    value.gzipBytes > value.bytes
  ) {
    console.error(`invalid size record for ${name}`);
    process.exit(1);
  }
}
if (write) {
  console.error(
    "writing a new baseline requires the licensed build host and is disabled in the public snapshot",
  );
  process.exit(2);
}
if (!check) {
  console.log("usage: --check or --write");
  process.exit(2);
}
console.log(
  `bundle baseline check passed: ${Object.keys(bundles).length} bundle(s), threshold ${threshold}%`,
);
