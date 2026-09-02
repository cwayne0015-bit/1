// Renders the weekly report as a single self-contained HTML document.
// Inline styles only (email clients strip <style>/external CSS). Colors and
// type trace back to DESIGN.md.

const C = {
  surface: "#fbfaf8",
  card: "#ffffff",
  text: "#1a1a1a",
  muted: "#5c5c5c",
  accent: "#0f766e",
  border: "#e7e4df",
  success: "#15803d",
  warning: "#b45309",
  danger: "#b91c1c",
};

const esc = (s) =>
  String(s ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");

function scoreColor(score) {
  if (score >= 60) return C.success;
  if (score >= 25) return C.warning;
  return C.danger;
}

function deltaBadge(d) {
  if (d.firstRun || d.scoreDelta == null) return "";
  const up = d.scoreDelta > 0;
  const flat = d.scoreDelta === 0;
  const color = flat ? C.muted : up ? C.success : C.danger;
  const arrow = flat ? "→" : up ? "▲" : "▼";
  return `<span style="color:${color};font-weight:700;font-size:15px;margin-left:8px;">${arrow} ${
    up ? "+" : ""
  }${d.scoreDelta} pts vs last week</span>`;
}

export function renderReport({ analysis, diff, fixkit }) {
  const a = analysis;
  const font =
    "-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Roboto,Helvetica,Arial,sans-serif";
  const sc = scoreColor(a.visibilityScore);

  const competitorList = a.topCompetitors.length
    ? a.topCompetitors
        .map(
          (c) =>
            `<li style="margin:4px 0;"><strong>${esc(c.name)}</strong> — named in ${
              c.count
            } answer${c.count === 1 ? "" : "s"}</li>`
        )
        .join("")
    : `<li style="color:${C.muted};">No competitors detected in the answers this week.</li>`;

  const rowsHtml = a.rows
    .map((r) => {
      const status = !r.checked
        ? `<span style="color:${C.muted};">not checked</span>`
        : r.youNamed
        ? `<span style="color:${C.success};font-weight:700;">✓ recommended</span>`
        : `<span style="color:${C.danger};font-weight:700;">✗ not named</span>`;
      const comps = r.competitorsNamed.length
        ? `<div style="color:${C.muted};font-size:12px;margin-top:2px;">instead: ${esc(
            r.competitorsNamed.join(", ")
          )}</div>`
        : "";
      return `<tr>
        <td style="padding:10px 8px;border-bottom:1px solid ${C.border};vertical-align:top;">
          <div>${esc(r.prompt)}</div>${comps}
        </td>
        <td style="padding:10px 8px;border-bottom:1px solid ${C.border};white-space:nowrap;">${esc(
        r.provider
      )}</td>
        <td style="padding:10px 8px;border-bottom:1px solid ${C.border};white-space:nowrap;">${status}</td>
      </tr>`;
    })
    .join("");

  const faqHtml = fixkit.faq
    .map(
      (f) => `<div style="margin:0 0 14px;">
        <div style="font-weight:700;">${esc(f.q)}</div>
        <div style="color:${C.muted};margin-top:2px;">${esc(f.a)}</div>
      </div>`
    )
    .join("");

  const reviewHtml = fixkit.reviewResponses
    .map(
      (r) => `<div style="margin:0 0 12px;">
        <div style="font-weight:700;font-size:13px;color:${C.muted};text-transform:uppercase;letter-spacing:.03em;">${esc(
        r.scenario
      )}</div>
        <div style="margin-top:2px;">${esc(r.text)}</div>
      </div>`
    )
    .join("");

  const schemaBlock = esc(
    `<script type="application/ld+json">\n` +
      JSON.stringify(fixkit.schema.business, null, 2) +
      `\n</script>\n<script type="application/ld+json">\n` +
      JSON.stringify(fixkit.schema.faq, null, 2) +
      `\n</script>`
  );

  const gbpQaHtml = fixkit.gbp.qa
    .map(
      (x) =>
        `<div style="margin:0 0 10px;"><strong>Q:</strong> ${esc(
          x.question
        )}<br><strong>A:</strong> ${esc(x.answer)}</div>`
    )
    .join("");

  const headline = a.visibilityScore === 0
    ? `AI assistants are <span style="color:${C.danger};">not recommending</span> ${esc(
        a.clinic.name
      )} yet.`
    : `${esc(a.clinic.name)} was recommended in <span style="color:${sc};">${
        a.timesNamed
      } of ${a.answersChecked}</span> AI answers.`;

  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GetCited weekly report — ${esc(a.clinic.name)}</title></head>
<body style="margin:0;background:${C.surface};color:${C.text};font-family:${font};line-height:1.6;">
<div style="max-width:680px;margin:0 auto;padding:24px;">

  <div style="font-weight:800;letter-spacing:-.02em;font-size:20px;color:${C.accent};">GetCited</div>
  <div style="color:${C.muted};font-size:13px;">Weekly AI-search visibility report · ${esc(
    a.clinic.city
  )} · ${esc(new Date(a.runAt).toLocaleDateString("en-US", { dateStyle: "medium" }))}</div>

  <div style="background:${C.card};border:1px solid ${C.border};border-radius:12px;padding:24px;margin:20px 0;">
    <div style="font-size:22px;font-weight:700;line-height:1.3;">${headline}${deltaBadge(diff)}</div>
    <div style="display:flex;gap:24px;margin-top:20px;flex-wrap:wrap;">
      <div>
        <div style="font-size:44px;font-weight:800;color:${sc};line-height:1;">${a.visibilityScore}%</div>
        <div style="color:${C.muted};font-size:13px;">AI visibility score</div>
      </div>
      <div style="flex:1;min-width:220px;">
        <div style="font-weight:700;margin-bottom:4px;">Who AI recommends instead:</div>
        <ul style="margin:0;padding-left:18px;">${competitorList}</ul>
      </div>
    </div>
  </div>

  <h2 style="font-size:18px;margin:28px 0 8px;">What we asked the AI assistants</h2>
  <table style="width:100%;border-collapse:collapse;font-size:14px;">
    <thead><tr>
      <th style="text-align:left;padding:8px;border-bottom:2px solid ${C.border};">Question a customer asks</th>
      <th style="text-align:left;padding:8px;border-bottom:2px solid ${C.border};">Engine</th>
      <th style="text-align:left;padding:8px;border-bottom:2px solid ${C.border};">Result</th>
    </tr></thead>
    <tbody>${rowsHtml}</tbody>
  </table>

  <div style="background:${C.accent};color:#fff;border-radius:12px;padding:20px 24px;margin:28px 0;">
    <div style="font-weight:800;font-size:18px;">Your Fix Kit — publish these to start getting cited</div>
    <div style="opacity:.9;font-size:14px;margin-top:4px;">AI assistants pull from structured data, FAQ content, and your Google Business Profile. Paste the items below; next week's report will show your movement.</div>
  </div>

  <h3 style="font-size:16px;margin:20px 0 8px;">1. FAQ block for your website</h3>
  ${faqHtml}

  <h3 style="font-size:16px;margin:24px 0 8px;">2. Schema markup (paste into your site &lt;head&gt;)</h3>
  <pre style="background:#0f1115;color:#e6e6e6;border-radius:8px;padding:16px;overflow:auto;font-size:12px;white-space:pre-wrap;">${schemaBlock}</pre>

  <h3 style="font-size:16px;margin:24px 0 8px;">3. Google Business Profile</h3>
  <div style="font-weight:700;">Business description:</div>
  <div style="color:${C.muted};margin:2px 0 12px;">${esc(fixkit.gbp.description)}</div>
  <div style="font-weight:700;">Suggested Q&amp;A to post:</div>
  <div style="margin-top:4px;">${gbpQaHtml}</div>

  <h3 style="font-size:16px;margin:24px 0 8px;">4. Review-response templates</h3>
  ${reviewHtml}

  <div style="border-top:1px solid ${C.border};margin-top:32px;padding-top:16px;color:${C.muted};font-size:12px;">
    GetCited optimizes the signals AI assistants use to recommend local businesses. Results vary and are not guaranteed.
    Reply to this email to talk to a human.
  </div>
</div>
</body></html>`;
}
