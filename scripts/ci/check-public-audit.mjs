#!/usr/bin/env node
import { readFile, readdir, stat } from "node:fs/promises";
import path from "node:path";

const root = path.resolve(process.argv[2] ?? ".");
const failures = [];
const read = (file) => readFile(path.join(root, file), "utf8");
const json = async (file) => JSON.parse(await read(file));

const versionProject = await read("CivicSurvival/CivicSurvival.csproj");
const manifest = await json("CivicSurvival/manifest.json");
const version = versionProject.match(/<Version>([^<]+)<\/Version>/)?.[1];
if (version !== manifest.version_number) failures.push(`version drift: project=${version} manifest=${manifest.version_number}`);
if (!manifest.website_url || manifest.website_url.includes("yourusername")) failures.push("manifest website URL is not canonical");

const privacy = await read("PRIVACY.md");
if (/opt[- ]out/i.test(privacy)) failures.push("privacy policy still uses opt-out diagnostics language");
if (!/opt-in, disabled by default/i.test(privacy)) failures.push("privacy policy must state diagnostics are opt-in and disabled by default");
for (const disclosed of ["ExceptionCode", "Phase"]) {
  if (!privacy.includes(disclosed)) failures.push(`privacy policy does not disclose crash field: ${disclosed}`);
}

for (const file of ["LICENSE", "NOTICE.md", "Assets/LICENSE", "Assets/README.md"]) {
  try { await stat(path.join(root, file)); } catch { failures.push(`missing license/notice file: ${file}`); }
}

const locales = ["en-US", "uk-UA", "zh-CN"];
const localeKeys = new Map();
for (const locale of locales) localeKeys.set(locale, scalarKeys(await json(`CivicSurvival/Localization/${locale}.json`)));
const baseline = localeKeys.get(locales[0]);
for (const locale of locales.slice(1)) {
  if (!sameSet(baseline, localeKeys.get(locale))) failures.push(`localization key drift: ${locale}`);
}

const policy = await json("scripts/ci/file-size-baseline.json");
const files = await collect(root, [".cs", ".ts", ".tsx"]);
let over500 = 0;
let over350 = 0;
for (const file of files) {
  const lines = (await readFile(file, "utf8")).split("\n").length;
  if (lines > 500) over500++;
  if (lines > 350) over350++;
}
if (over500 > policy.over500 || over350 > policy.over350) {
  failures.push(`file-size regression: >500 ${over500}/${policy.over500}, >350 ${over350}/${policy.over350}`);
}

if (failures.length) {
  console.error(failures.map((failure) => `ERROR ${failure}`).join("\n"));
  process.exit(1);
}
console.log(JSON.stringify({ status: "pass", version, localizationKeys: baseline.size, over500, over350 }));

function scalarKeys(value, prefix = "") {
  const output = new Set();
  if (!value || typeof value !== "object" || Array.isArray(value)) return output;
  for (const [key, child] of Object.entries(value)) {
    const full = prefix ? `${prefix}.${key}` : key;
    if (child && typeof child === "object" && !Array.isArray(child)) {
      for (const nested of scalarKeys(child, full)) output.add(nested);
    } else output.add(full);
  }
  return output;
}

function sameSet(left, right) {
  return left.size === right.size && [...left].every((key) => right.has(key));
}

async function collect(directory, suffixes) {
  const output = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if ([".git", "node_modules", "bin", "obj", "dist"].includes(entry.name)) continue;
    const full = path.join(directory, entry.name);
    if (entry.isDirectory()) output.push(...await collect(full, suffixes));
    else if (suffixes.some((suffix) => entry.name.endsWith(suffix))) output.push(full);
  }
  return output;
}
