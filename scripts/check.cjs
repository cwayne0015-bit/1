#!/usr/bin/env node
/* Lightweight structural smoke test for the single-file creatorOS app.
   No build/test framework exists for a static HTML app, so this guards
   the realistic regressions: a removed component, a broken <script>,
   stripped monetization config, or an unresolved merge conflict. */
"use strict";
const fs = require("fs");
const path = require("path");

const file = process.argv[2] || path.join(__dirname, "..", "index.html");
const fails = [];
const ok = (cond, msg) => { if (!cond) fails.push(msg); };

let html = "";
try { html = fs.readFileSync(file, "utf8"); }
catch { console.error("FAIL: cannot read " + file); process.exit(1); }

ok(html.length > 20000, "index.html is suspiciously small (" + html.length + " bytes)");
ok(!/^(<{7}|={7}|>{7})/m.test(html), "unresolved git merge conflict markers present");
ok(html.includes('<div id="root">'), 'missing React mount point <div id="root">');

const opens = (html.match(/<script\b/g) || []).length;
const closes = (html.match(/<\/script>/g) || []).length;
ok(opens === closes && opens >= 4, `unbalanced <script> tags (${opens} open / ${closes} close)`);

for (const lib of ["react@18/umd/react.production", "react-dom@18/umd/react-dom.production", "@babel/standalone/babel"]) {
  ok(html.includes(lib), "missing CDN dependency: " + lib);
}
ok(/<script type="text\/babel"[^>]*data-presets="react"/.test(html),
   'babel script must declare data-presets="react"');

const m = html.match(/<script type="text\/babel"[^>]*>([\s\S]*?)<\/script>/);
ok(!!m, "could not locate the text/babel application block");
const js = m ? m[1] : "";

const required = [
  "function App(", "function Onboarding(", "function Generate(", "function Plan(",
  "function Vault(", "function ProfileView(", "function SettingsModal(",
  "function UpgradeModal(", "function IdeaCard(", "function IdeaModal(",
  "function parseIdeas(", "async function generateIdeas(", "ReactDOM.createRoot",
];
for (const sym of required) ok(js.includes(sym), "missing app symbol: " + sym);

// Monetization wiring must survive any future edit.
ok(js.includes("STRIPE_PAYMENT_LINK"), "missing STRIPE_PAYMENT_LINK config");
ok(js.includes("FREE_GENERATION_LIMIT"), "missing FREE_GENERATION_LIMIT config");
ok(/upgraded.*===.*"1"|"upgraded"\)===/.test(js) || js.includes('q.get("upgraded")'),
   "missing Stripe ?upgraded=1 unlock path");
ok(js.includes("api.anthropic.com/v1/messages"), "missing Claude API endpoint");

if (fails.length) {
  console.error("creatorOS check: FAILED");
  for (const f of fails) console.error("  - " + f);
  process.exit(1);
}
console.log("creatorOS check: OK (" + required.length + " components + monetization + deps verified)");
