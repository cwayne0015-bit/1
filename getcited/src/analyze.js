// Turn raw AI answers into a visibility scorecard for one clinic.
// Detection is deliberately simple and explainable: case-insensitive,
// word-boundary name matching. No black box — the owner can trust the count.

function mentions(text, name) {
  if (!text || !name) return false;
  // Escape regex specials, match on a loose word boundary so "Glow Aesthetics"
  // matches inside a sentence but "Glowy" doesn't match "Glow".
  const esc = name.trim().replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`(^|[^a-z0-9])${esc}([^a-z0-9]|$)`, "i").test(text);
}

// Fill a prompt template with the clinic's city + a treatment.
export function expandPrompts(clinic) {
  const treatments = clinic.treatments?.length ? clinic.treatments : ["treatments"];
  const out = [];
  for (const tmpl of clinic.prompts || []) {
    if (tmpl.includes("{treatment}")) {
      // Use the first 2 treatments to keep query volume (and cost) bounded.
      for (const t of treatments.slice(0, 2)) {
        out.push(tmpl.replaceAll("{treatment}", t).replaceAll("{city}", clinic.city));
      }
    } else {
      out.push(tmpl.replaceAll("{city}", clinic.city));
    }
  }
  return [...new Set(out)];
}

// results: [{ provider, prompt, text }]
export function analyze(clinic, results) {
  const competitors = clinic.competitors || [];
  const rows = results.map((r) => {
    const named = mentions(r.text, clinic.name);
    const namedCompetitors = competitors.filter((c) => mentions(r.text, c));
    return {
      provider: r.provider,
      prompt: r.prompt,
      checked: r.text != null,
      youNamed: named,
      competitorsNamed: namedCompetitors,
    };
  });

  const checked = rows.filter((r) => r.checked);
  const youCount = checked.filter((r) => r.youNamed).length;
  const total = checked.length || 1;
  const visibilityScore = Math.round((youCount / total) * 100);

  // Which competitors show up most across all answers — your real AI rivals.
  const compTally = {};
  for (const r of checked) {
    for (const c of r.competitorsNamed) compTally[c] = (compTally[c] || 0) + 1;
  }
  const topCompetitors = Object.entries(compTally)
    .sort((a, b) => b[1] - a[1])
    .map(([name, count]) => ({ name, count }));

  return {
    clinic: { id: clinic.id, name: clinic.name, city: clinic.city },
    runAt: new Date().toISOString(),
    visibilityScore, // 0-100: % of checked answers that named the clinic
    answersChecked: checked.length,
    timesNamed: youCount,
    topCompetitors,
    rows,
  };
}

// Compare this run to the previous snapshot for week-over-week deltas.
export function diff(current, previous) {
  if (!previous) {
    return { scoreDelta: null, firstRun: true, newlyLost: [], newlyWon: [] };
  }
  const prevByPrompt = new Map(
    previous.rows.map((r) => [`${r.provider}::${r.prompt}`, r.youNamed])
  );
  const newlyWon = [];
  const newlyLost = [];
  for (const r of current.rows) {
    const k = `${r.provider}::${r.prompt}`;
    if (!prevByPrompt.has(k)) continue;
    const was = prevByPrompt.get(k);
    if (!was && r.youNamed) newlyWon.push(r);
    if (was && !r.youNamed) newlyLost.push(r);
  }
  return {
    firstRun: false,
    scoreDelta: current.visibilityScore - previous.visibilityScore,
    newlyWon,
    newlyLost,
  };
}
