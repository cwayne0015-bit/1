# Instagram Content Calendar — Automation Playbook
**Google Calendar as the queue · human approval gate · Canva for media · Zapier for publishing**

> Scope note: This playbook covers the **mechanics** of drafting, approving, and publishing Instagram content on a schedule for a faceless, monetized page. It is independent of any other project in this repo. The account is @Precision.Motivation (§6); §7 covers the account risk that determines whether this pipeline is safe to run at volume.

---

## 1. Why the approval gate lives in Google Calendar

Instagram's Content Publishing API has **no draft state and no native scheduling**. The Zapier integration exposes exactly three write actions:

| Action | Zapier name | Purpose |
|---|---|---|
| `publish_media_v2` | Publish Photo(s) | Photos and carousels |
| `publish_video` | Publish Video | Video |
| `_zap_raw_request` | Make API GET / Mutating Request | Raw Graph API passthrough |

Confirmed parameters (both publish actions share the same shape):

| Param | Notes |
|---|---|
| `media` / `video` | **Required.** Public `https://` URL or file. Photos: `jpg`, `gif`, `png`, `ico`, `bmp` — **no webp**. Video: `mp4`, `mov`, and similar. |
| `caption` | Up to **2,200 characters**; emoji, hashtags, and line breaks allowed. |
| `instagramPageId` | **Required.** Dynamic enum — resolvable only once an account is connected. |
| `location` | Optional place name, fuzzy-matched. |
| `tagged_users` | Optional list of public `@handles`. |

**Carousels are `publish_media_v2` with 1–10 URLs in `media`** — there is no separate carousel action.

**There is no Reels flag.** `publish_video` publishes a video; Instagram decides placement. Treat Reels as the expected outcome of posting vertical video, not as something this API selects.

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
   - Else export the Canva design (`export-design` — `jpg` for feed/carousel, `mp4` for reels) and use the returned URL. Call `get-export-formats` first; not every design supports every format.
4. Call `publish_media_v2` (feed/carousel) or `publish_video` (reel).
5. Rename the event to `[IG-DONE]` and append the permalink to `--- STATUS ---`.

**Export at publish time, not draft time.** Canva export URLs are short-lived; a URL generated during drafting will be dead by the time the slot arrives. This is the single most likely cause of silent publish failures.

If a publish call fails, leave the prefix at `[IG-OK]` and append the error to `--- STATUS ---`. The next run retries it. Never mark `[IG-DONE]` on a failed call.

---

## 6. Content model — faceless page

The account is a faceless page built to generate income. That shapes the pipeline in three ways.

### Reels are the growth engine

Faceless pages grow through Reels, not static posts — the feed rewards video to non-followers, which is the only way an account with no personal brand reaches new people. `publish_video` covers this, with the caveat in §1: the call publishes video and Instagram decides placement, so the lever you control is the asset itself. Vertical 9:16 under 90 seconds is what lands as a Reel.

Static posts and carousels still matter for profile depth and saves, but they do not drive discovery. Plan the mix roughly **70% Reels / 30% carousel-or-static**.

### The Canva video path

Canva exports MP4, so the pipeline is: Canva video design → export MP4 → `publish_video`. Two caveats beyond the general export rule in §5:

- Video export is **asynchronous and slower than image export** — the publisher must poll for completion before calling Instagram.
- Instagram fetches the MP4 from the URL itself, so the export URL must still be live when the publish call runs. Reinforces export-at-publish-time.

### Account and offer

**@Precision.Motivation** — motivation, wealth, success, personal growth. Monetized through a digital product.

The product already exists in this repo: **The Launch Playbook**, $39 (anchored against $79), "ship your first profitable digital product in 30 days," with a Jekyll sales page, Stripe checkout, a `/success/` page, and the deliverable in `downloads/`. The offer topic sits squarely inside the niche, so the funnel is coherent: Reel → profile link → sales page → Stripe → download.

**The checkout is not live yet.** In `_config.yml`, `stripe_payment_link` is still the placeholder `"#get"`, `formspree_id` is `"your-form-id"`, and `url`/`baseurl` are empty. Traffic sent today lands on a page whose buy button goes nowhere. Fix this before the offer pillar runs — everything else is upstream of a dead link.

### Being original in this niche

The niche's conventional format — clipped speeches, podcast segments, movie scenes — is the §7 failure case, and this pipeline must not use it. The alternative is fully automatable and just as fast:

- **Your script, rendered.** Original writing as kinetic text over **licensed** stock footage, built in Canva and exported to MP4. The words are yours, so there is nothing to strike or demote.
- **AI voiceover is fine over an original script.** The originality that matters is authorship of the ideas, not whose voice reads them.
- **Never** repost another creator's Reel, rip podcast or speech audio, or use film clips — regardless of credit given in the caption.

This keeps the whole pipeline automatable while staying clear of the reach penalty.

### Pillars

Rotate rather than repeat. Adjust once early performance data exists.

1. **Mindset reframe** *(Reel)* — a counterintuitive take on discipline, failure, or consistency. Broadest reach; top of funnel.
2. **Money mechanics** *(Reel or carousel)* — concrete and teachable: how a digital product actually earns, pricing, what the first sale looks like. Bridges motivation to the offer.
3. **Systems and habits** *(Reel)* — routines, focus, execution. Strong saves; builds the personal-growth half of the positioning.
4. **Proof or case** *(carousel)* — a breakdown of a real zero-to-first-sale path. Must be genuine and substantiated per §7.
5. **Direct offer** *(carousel or static)* — The Launch Playbook. Roughly one in six posts.

## 7. Originality and account risk

**This is the main threat to a fully-automated faceless page, and it is worth understanding before investing in the pipeline.**

Meta actively demotes unoriginal content. Accounts that repeatedly post others' material without meaningful transformation get reach-limited, and duplicate content can be replaced in the feed by a link to the original creator. Repurposing viral clips — the default faceless playbook — is precisely the behavior being targeted. Aggressive reposting also risks copyright strikes and, at the far end, account loss.

The automation is indifferent to this. It will publish whatever it is handed, at scale, which means a bad content source turns a working pipeline into a fast way to burn an account.

**Practical line:** automate *distribution*, not *sourcing*. Content should be original or substantially transformed — your own script, your own edit, your own voiceover or text treatment — even when the visuals are stock. Stock footage under a proper license is fine; someone else's Reel with a new caption is not.

### Monetization reality

The pipeline does not produce income; the offer does. Realistic paths, roughly in order of accessibility:

- **Affiliate marketing** — the usual starting point for faceless pages.
- **Your own digital product** — highest margin, requires something to sell.
- **Brand deals** — needs meaningful audience first, and a niche brands want to reach.
- **Meta bonus programs** — invite-based and inconsistent; do not plan around them.

Expect months, not weeks, before any of these produce meaningful revenue. Niche choice affects earnings far more than posting cadence does.

### Disclosure

- **Affiliate links and sponsorships require clear disclosure.** This is an FTC requirement, not an Instagram nicety.
- **Substantiate claims.** Income figures, results, and timelines shown in content must be real and defensible.
- **DM funnels are lead capture.** A "DM the keyword" call to action collects contacts; consent obtained there does not extend to cold calling or texting them.

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
- [x] Account identified — @Precision.Motivation (§6)
- [x] Content pillars drafted (§6)
- [ ] Configure Stripe payment link and Formspree ID in _config.yml (§6)
- [ ] Set url/baseurl and enable GitHub Pages for the sales site
- [ ] Settle the content source — original vs. transformed (§7)
- [ ] Canva template built for recurring post formats
- [ ] Publishing schedule armed (§5)
