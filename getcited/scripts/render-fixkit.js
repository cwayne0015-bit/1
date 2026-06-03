// Render a standalone Fix Kit HTML for one clinic (no visibility scan).
// Usage: node scripts/render-fixkit.js <clinicId> <outFile>
import { readFileSync, writeFileSync } from "node:fs";
import { buildFixKit } from "../src/fixkit.js";

const [, , clinicId, outFile] = process.argv;
const cfg = JSON.parse(readFileSync(new URL("../config/clinics.json", import.meta.url), "utf8"));
const clinic = cfg.clinics.find((c) => c.id === clinicId) || cfg.clinics[0];
const k = buildFixKit(clinic);

const esc = (s) =>
  String(s).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
const C = { surface: "#fbfaf8", muted: "#5c5c5c", accent: "#0f766e", border: "#e7e4df" };
const font = "-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Roboto,Helvetica,Arial,sans-serif";

const faq = k.faq
  .map(
    (f) =>
      `<div style="margin:0 0 14px"><div style="font-weight:700">${esc(
        f.q
      )}</div><div style="color:${C.muted};margin-top:2px">${esc(f.a)}</div></div>`
  )
  .join("");
const rev = k.reviewResponses
  .map(
    (r) =>
      `<div style="margin:0 0 12px"><div style="font-weight:700;font-size:13px;color:${C.muted};text-transform:uppercase;letter-spacing:.03em">${esc(
        r.scenario
      )}</div><div style="margin-top:2px">${esc(r.text)}</div></div>`
  )
  .join("");
const gbpqa = k.gbp.qa
  .map(
    (x) =>
      `<div style="margin:0 0 10px"><strong>Q:</strong> ${esc(
        x.question
      )}<br><strong>A:</strong> ${esc(x.answer)}</div>`
  )
  .join("");
const tag = "script";
const schema = esc(
  `<${tag} type="application/ld+json">\n` +
    JSON.stringify(k.schema.business, null, 2) +
    `\n</${tag}>\n<${tag} type="application/ld+json">\n` +
    JSON.stringify(k.schema.faq, null, 2) +
    `\n</${tag}>`
);

const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GetCited Fix Kit — ${esc(
  clinic.name
)}</title></head>
<body style="margin:0;background:${C.surface};color:#1a1a1a;font-family:${font};line-height:1.6">
<div style="max-width:680px;margin:0 auto;padding:24px">
<div style="font-weight:800;font-size:20px;color:${C.accent}">GetCited</div>
<div style="color:${C.muted};font-size:13px">AI-visibility Fix Kit · ${esc(clinic.name)} · ${esc(
  clinic.city
)}</div>
<div style="background:${C.accent};color:#fff;border-radius:12px;padding:20px 24px;margin:18px 0">
<div style="font-weight:800;font-size:18px">Your Fix Kit — publish these to get recommended by AI</div>
<div style="opacity:.9;font-size:14px;margin-top:4px">AI assistants (ChatGPT, Perplexity, Gemini) pull from structured data, FAQ content, and your Google Business Profile. Paste the items below; they make ${esc(
  clinic.name
)} citable.</div></div>
<h3 style="font-size:16px;margin:20px 0 8px">1. FAQ block for ${esc(clinic.website)}</h3>${faq}
<h3 style="font-size:16px;margin:24px 0 8px">2. Schema markup (paste into your site &lt;head&gt;)</h3>
<pre style="background:#0f1115;color:#e6e6e6;border-radius:8px;padding:16px;overflow:auto;font-size:12px;white-space:pre-wrap">${schema}</pre>
<h3 style="font-size:16px;margin:24px 0 8px">3. Google Business Profile</h3>
<div style="font-weight:700">Business description:</div><div style="color:${C.muted};margin:2px 0 12px">${esc(
  k.gbp.description
)}</div>
<div style="font-weight:700">Suggested Q&amp;A to post:</div><div style="margin-top:4px">${gbpqa}</div>
<h3 style="font-size:16px;margin:24px 0 8px">4. Review-response templates</h3>${rev}
<div style="border-top:1px solid ${C.border};margin-top:32px;padding-top:16px;color:${C.muted};font-size:12px">GetCited optimizes the signals AI assistants use to recommend local businesses. Results vary and are not guaranteed.</div>
</div></body></html>`;

writeFileSync(outFile, html);
console.log(
  `Fix Kit → ${outFile} | FAQ ${k.faq.length} | GBP desc ${k.gbp.description.length} chars | ${k.reviewResponses.length} review templates`
);
