// Sends a report via Resend's REST API using built-in fetch (no SDK).
// Returns true if sent, false if not configured or on error (never throws —
// a failed email must not break the weekly run; the HTML is also saved to disk).

export async function sendReport({ to, subject, html }) {
  const key = process.env.RESEND_API_KEY;
  const from = process.env.REPORT_FROM;
  if (!key || !from) {
    console.warn("  [email] RESEND_API_KEY / REPORT_FROM not set — skipping send");
    return false;
  }
  try {
    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        authorization: `Bearer ${key}`,
      },
      body: JSON.stringify({ from, to, subject, html }),
    });
    if (!res.ok) {
      console.warn(`  [email] Resend ${res.status}: ${await res.text()}`);
      return false;
    }
    return true;
  } catch (e) {
    console.warn(`  [email] ${e.message}`);
    return false;
  }
}
