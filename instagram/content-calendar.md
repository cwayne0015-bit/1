# Instagram Content Calendar — Automation Playbook
**Google Calendar as the queue · human approval gate · Canva for media · Zapier for publishing**

> Scope note: This playbook covers the **mechanics** of drafting, approving, and publishing Instagram content on a schedule. It is independent of any other project in this repo. Content strategy (§6) is not yet defined — it depends on the account's brand.

---

## 1. Why the approval gate lives in Google Calendar

Instagram's Content Publishing API has **no draft state and no native scheduling**. The Zapier integration exposes exactly three write actions:

| Action | Purpose |
|---|---|
| `publish_media_v2` | Photos and carousels |
| `publish_video` | Video and Reels |
| `_zap_raw_request` | Raw Graph API passthrough |

Both real actions publish **immediately** on call. There is no server-side "pending" state to review.

A two-step container flow via `_zap_raw_request` (create media container, publish later) technically holds unpublished media, but containers expire roughly 24 hours after creation — useless for a calendar drafted days ahead.

**Therefore the gate is upstream.** A post that has not been approved is never handed to Instagram at all. Approval is a state on the calendar event, not a state in Instagram.

---

## 2. Account prerequisites

Instagram has no API for personal accounts. Publishing requires:

1. An Instagram **Professional** account (Business or Creator) — switch under Settings → Account type and tools.
2. A linked **Facebook Page**.
3. That account authorized in Zapier: https://mcp.zapier.com/api/v1/connect-auth/InstagramBusinessCLIAPI

Until step 3 completes, the drafting half of this pipeline runs and the publishing half is inert. That is the intended failure mode — drafts accumulate, nothing posts.

---

## 3. The calendar contract

All state lives in the event itself, so it is reviewable and editable from the Google Calendar mobile app with no extra tooling.

**Calendar:** `precisionconstructionsil@gmail.com` (currently the only connected calendar)

**Timezone:** always write events with an explicit `timeZone: America/Chicago`. The calendar's own default is **UTC** — omitting the field lands posts six hours off.

### Title prefix carries approval state

| Prefix | Meaning | Publisher behavior |
|---|---|---|
| `[IG-DRAFT]` | Awaiting review | **Skipped.** Never published. |
| `[IG-OK]` | Approved | Published at event start time. |
| `[IG-DONE]` | Already published | Skipped; carries the resulting permalink. |
| `[IG-HOLD]` | Explicitly pulled | Skipped indefinitely. |

Approving a post is renaming one prefix. Default-deny: anything unrecognized is skipped, so a typo fails safe.

### Description schema

```
--- CAPTION ---
<caption text exactly as it should post, hashtags included>

--- MEDIA ---
canva_design_id: <D-prefixed design id, or blank>
media_url: <public URL, overrides canva_design_id if set>
post_type: feed | reel | carousel

--- STATUS ---
<free notes; publisher appends permalink and timestamp here>
```

Other conventions:
- **Event start time = intended publish time.** Duration is cosmetic; use 15 minutes.
- Set `availability: FREE` so content slots never block real scheduling.
- Use a consistent `colorId` so content is visually distinct from other calendar entries.

---

## 4. Drafting cycle

Runs ahead of the posting week. For each planned slot:

1. Pick the pillar (§6) and the specific angle.
2. Write the caption into the `--- CAPTION ---` block.
3. Generate the visual in Canva; record the design ID under `canva_design_id`. **Do not export yet** — see §5.
4. Create the event as `[IG-DRAFT]` at the intended publish time.

Review happens in the calendar. Edit the caption in place, then rename the prefix to `[IG-OK]`.

---

## 5. Publishing cycle

Runs on a schedule (hourly is sufficient for slot-level precision):

1. List events on the calendar in the window now → now + interval.
2. Keep only titles beginning `[IG-OK]`.
3. For each: resolve media.
   - If `media_url` is set, use it.
   - Else export the Canva design (`export-design`, `jpg`) and use the returned URL.
4. Call `publish_media_v2` (feed/carousel) or `publish_video` (reel).
5. Rename the event to `[IG-DONE]` and append the permalink to `--- STATUS ---`.

**Export at publish time, not draft time.** Canva export URLs are short-lived; a URL generated during drafting will be dead by the time the slot arrives. This is the single most likely cause of silent publish failures.

If a publish call fails, leave the prefix at `[IG-OK]` and append the error to `--- STATUS ---`. The next run retries it. Never mark `[IG-DONE]` on a failed call.

---

## 6. Content pillars

**Not yet defined** — pending confirmation of which brand this account represents.

Fill this in with 4–5 recurring post types before the first drafting run, so the calendar rotates rather than repeats.

---

## 7. Advertising basics

Applies to any commercial account:

- **Substantiate claims.** Stated results, timelines, and figures must be real and defensible. Screenshotted "results" are advertising claims.
- **Disclose material connections.** Paid partnerships, affiliate links, and sponsorships need clear disclosure.
- **DM funnels are lead capture.** A "DM the keyword" call to action collects contacts. Consent obtained there does not automatically extend to calling or texting those people.

Regulated industries carry additional rules on top of this. Revisit once §6 is defined.

---

## 8. Known constraints

- **Stories and DMs are not publishable via API.** Feed photos, carousels, videos, and Reels only. Anything Story-based stays manual.
- **Media must be at a public URL.** Instagram fetches it server-side. Google Drive share links do not work as direct media URLs.
- **Meta enforces a publishing rate limit** (on the order of 25 posts per 24 hours per account). Not a real constraint at normal cadence, but relevant to any backfill.
- **Single calendar.** All content shares a calendar with other events; the `[IG-*]` prefix is the only separator. A dedicated calendar would be cleaner if the Google account gains one.
- **No Canva brand kit is configured.** Designs are generated without a stored brand identity, so visual consistency depends on reusing a template rather than a brand kit.

---

## 9. Setup checklist

- [ ] Instagram switched to Professional (Business or Creator)
- [ ] Facebook Page linked to the Instagram account
- [ ] Instagram authorized in Zapier (§2, step 3)
- [ ] Confirm which brand/entity the account represents
- [ ] Define content pillars (§6)
- [ ] Canva template built for recurring post formats
- [ ] Publishing schedule armed (§5)
