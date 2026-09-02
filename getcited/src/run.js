// GetCited weekly run.
//
//   node src/run.js                         # uses config/clinics.json, emails reports
//   node src/run.js --config <file>         # custom clinic config
//   node src/run.js --out <dir>             # also write HTML reports to <dir>
//   node src/run.js --dry-run               # no API calls, simulated answers, no email
//                                           # (use this to generate a sample report)
//
// Snapshots are stored in data/<clinic-id>.json for week-over-week diffs.

import { readFile, writeFile, mkdir, readdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import { PROVIDERS } from "./providers.js";
import { analyze, diff, expandPrompts } from "./analyze.js";
import { buildFixKit } from "./fixkit.js";
import { renderReport } from "./report.js";
import { sendReport } from "./email.js";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");

function arg(flag, fallback) {
  const i = process.argv.indexOf(flag);
  if (i === -1) return fallback;
  const next = process.argv[i + 1];
  return next && !next.startsWith("--") ? next : true;
}
const DRY = process.argv.includes("--dry-run");
const CONFIG = arg("--config", "config/clinics.json");
const OUT = arg("--out", DRY ? "samples" : "out");

// Load a .env file if present (tiny parser; no dependency).
async function loadEnv() {
  const p = path.join(ROOT, ".env");
  if (!existsSync(p)) return;
  const txt = await readFile(p, "utf8");
  for (const line of txt.split("\n")) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
    if (m && !process.env[m[1]]) {
      process.env[m[1]] = m[2].replace(/^["']|["']$/g, "");
    }
  }
}

// In dry-run we fabricate a realistic answer: competitors get named, the clinic
// usually doesn't — exactly the "you're invisible" state used to pre-sell.
function mockAnswer(clinic) {
  const comps = clinic.competitors || ["A Local Clinic", "Another Spa"];
  return `For aesthetic treatments in ${clinic.city}, popular and well-reviewed options include ${comps
    .slice(0, 2)
    .join(" and ")}. Both are frequently recommended. Be sure to book a consultation first.`;
}

async function gather(clinic) {
  const prompts = expandPrompts(clinic);
  const results = [];
  for (const prompt of prompts) {
    for (const p of PROVIDERS) {
      if (DRY) {
        results.push({ provider: p.key, prompt, text: mockAnswer(clinic) });
        continue;
      }
      if (!process.env[p.env]) {
        results.push({ provider: p.key, prompt, text: null }); // not checked
        continue;
      }
      const text = await p.ask(prompt);
      results.push({ provider: p.key, prompt, text });
    }
  }
  return results;
}

async function loadPrevious(clinicId) {
  const p = path.join(ROOT, "data", `${clinicId}.json`);
  if (!existsSync(p)) return null;
  try {
    return JSON.parse(await readFile(p, "utf8"));
  } catch {
    return null;
  }
}

async function main() {
  await loadEnv();
  const cfgPath = path.isAbsolute(CONFIG) ? CONFIG : path.join(ROOT, CONFIG);
  if (!existsSync(cfgPath)) {
    console.error(`Config not found: ${cfgPath}`);
    console.error("Copy config/clinics.example.json to config/clinics.json and edit it.");
    process.exit(1);
  }
  const { clinics } = JSON.parse(await readFile(cfgPath, "utf8"));
  if (!clinics?.length) {
    console.error("No clinics in config.");
    process.exit(1);
  }

  await mkdir(path.join(ROOT, "data"), { recursive: true });
  const outDir = path.isAbsolute(OUT) ? OUT : path.join(ROOT, OUT);
  await mkdir(outDir, { recursive: true });

  console.log(`GetCited run${DRY ? " (dry-run, simulated)" : ""} — ${clinics.length} clinic(s)\n`);

  for (const clinic of clinics) {
    console.log(`→ ${clinic.name} (${clinic.city})`);
    const results = await gather(clinic);
    const current = analyze(clinic, results);
    const previous = await loadPrevious(clinic.id);
    const d = diff(current, previous);
    const fixkit = buildFixKit(clinic);
    const html = renderReport({ analysis: current, diff: d, fixkit });

    const file = path.join(outDir, `${clinic.id}.html`);
    await writeFile(file, html);
    console.log(
      `  visibility ${current.visibilityScore}% (named ${current.timesNamed}/${current.answersChecked}) → ${path.relative(
        ROOT,
        file
      )}`
    );

    if (!DRY) {
      // Persist snapshot for next week's diff.
      await writeFile(
        path.join(ROOT, "data", `${clinic.id}.json`),
        JSON.stringify(current, null, 2)
      );
      if (clinic.email) {
        const subject = `Your AI visibility report — ${current.visibilityScore}% this week`;
        const sent = await sendReport({ to: clinic.email, subject, html });
        console.log(`  email → ${clinic.email}: ${sent ? "sent" : "skipped"}`);
      }
    }
  }
  console.log(`\nDone. Reports in ${path.relative(ROOT, outDir)}/`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
