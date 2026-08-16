# Changelog

All notable changes to **Show Me The Money** are documented here. The README
front page covers only the current release; older notes live here.

Format follows [Keep a Changelog](https://keepachangelog.com/) loosely, and the
project uses semantic-ish versioning.

[English](CHANGELOG.md) | [中文](CHANGELOG.zh-CN.md)

---

## v2.5.1 — 2026-05-12

Small but noticeable fixes following the v2.5.0 ship.

- **Value Quantification blocks now render correctly in terminal markdown
  viewers.** The previous empty-header two-column tables (`| | |`) collapsed to
  "Column 1 / Column 2" prose in Claude Code's terminal renderer. Converted
  across 13 SKILL.md files to a bulleted list with a bold prefix — renders
  cleanly in terminal, GitHub, and every other markdown viewer.
- Added an explicit rule in `/money`'s template that forbids reintroducing the
  empty-header form.
- **"What's New" history split into a dedicated changelog.** Older release notes
  lived inline in the README and were getting long; they now live here (and in
  [CHANGELOG.zh-CN.md](CHANGELOG.zh-CN.md) for the Chinese version).

---

## v2.5.0 — 2026-05-11

- **Business-type awareness (7 types).** Skills now adapt their frameworks to the
  kind of business being built (e.g. API, dev tool, consumer app, content,
  marketplace, service, info-product) instead of assuming one shape.
- **`/money-strategy iterate`** — a post-PMF iteration mode that skips greenfield
  framing, identifies the current binding constraint, and forms one hypothesis
  to relax it.

---

## v2.4.0 — 2026-05-10

- **Operating modes** for `/money-ops` (open / staging / production) with an
  edit perimeter and a panic stop.
- **Narrowest-bet** statement added as the required output of `/money-discover`.
- **Ship lifecycle** in `/money-product`: VERSION + CHANGELOG + release notes.
- **STRIDE** threat modeling added to `/money-quality` alongside OWASP.
- **Portfolio learnings** shared across every project in `/money-learn`.
- **Auto-update** via `/money-upgrade`.

---

## v2.3.1 — 2026-05-03

- Founder-atom polish, per-skill callouts, and a workflow fix.

---

## v2.3.0 — 2026-05-03

- **Founder atoms** knowledge base — small, reusable, composable learnings.

---

## v2.2.0 — 2026-04

- **Review panel** (`/money-panel`) plus the four reviewers.
- **Cross-session learning** foundations.

---

## v2.1.0

- **Cross-session state management** — `/money-save`, `/money-restore`,
  `/money-report`.
