// Thin wrappers over the three AI answer engines. Each returns the assistant's
// text for a single prompt, or null if the provider isn't configured / errored.
// No SDKs — just built-in fetch (Node 18+), so there's nothing to `npm install`.

const TIMEOUT_MS = 30_000;

async function withTimeout(promise) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  try {
    return await promise(ctrl.signal);
  } finally {
    clearTimeout(t);
  }
}

export async function askOpenAI(prompt) {
  const key = process.env.OPENAI_API_KEY;
  if (!key) return null;
  const model = process.env.OPENAI_MODEL || "gpt-4o-mini";
  try {
    return await withTimeout(async (signal) => {
      const res = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        signal,
        headers: {
          "content-type": "application/json",
          authorization: `Bearer ${key}`,
        },
        body: JSON.stringify({
          model,
          messages: [{ role: "user", content: prompt }],
          temperature: 0.3,
        }),
      });
      if (!res.ok) throw new Error(`OpenAI ${res.status}`);
      const j = await res.json();
      return j.choices?.[0]?.message?.content ?? "";
    });
  } catch (e) {
    console.warn(`  [openai] ${e.message}`);
    return null;
  }
}

export async function askGemini(prompt) {
  const key = process.env.GEMINI_API_KEY;
  if (!key) return null;
  const model = process.env.GEMINI_MODEL || "gemini-2.0-flash";
  try {
    return await withTimeout(async (signal) => {
      const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${key}`;
      const res = await fetch(url, {
        method: "POST",
        signal,
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
        }),
      });
      if (!res.ok) throw new Error(`Gemini ${res.status}`);
      const j = await res.json();
      return j.candidates?.[0]?.content?.parts?.map((p) => p.text).join("") ?? "";
    });
  } catch (e) {
    console.warn(`  [gemini] ${e.message}`);
    return null;
  }
}

export async function askPerplexity(prompt) {
  const key = process.env.PERPLEXITY_API_KEY;
  if (!key) return null;
  const model = process.env.PERPLEXITY_MODEL || "sonar";
  try {
    return await withTimeout(async (signal) => {
      const res = await fetch("https://api.perplexity.ai/chat/completions", {
        method: "POST",
        signal,
        headers: {
          "content-type": "application/json",
          authorization: `Bearer ${key}`,
        },
        body: JSON.stringify({
          model,
          messages: [{ role: "user", content: prompt }],
          temperature: 0.3,
        }),
      });
      if (!res.ok) throw new Error(`Perplexity ${res.status}`);
      const j = await res.json();
      return j.choices?.[0]?.message?.content ?? "";
    });
  } catch (e) {
    console.warn(`  [perplexity] ${e.message}`);
    return null;
  }
}

// Ordered list of providers we attempt. Label is what shows in the report.
export const PROVIDERS = [
  { key: "ChatGPT", env: "OPENAI_API_KEY", ask: askOpenAI },
  { key: "Gemini", env: "GEMINI_API_KEY", ask: askGemini },
  { key: "Perplexity", env: "PERPLEXITY_API_KEY", ask: askPerplexity },
];
