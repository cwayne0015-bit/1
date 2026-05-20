"""Command-line interface for igkit.

Examples:
  python -m igkit.cli content captions --brand brand.json --topic "summer launch"
  python -m igkit.cli content ideas    --brand brand.json --theme "behind the scenes"
  python -m igkit.cli schedule add --at 2026-05-20T09:00:00+00:00 \
        --type image --media https://cdn/img.jpg --caption "hello"
  python -m igkit.cli schedule run
  python -m igkit.cli schedule list
  python -m igkit.cli links add --slug shop --url https://shop.example/p/1 --type product
  python -m igkit.cli links utm --url https://blog.example/post --campaign launch
  python -m igkit.cli links bio --out bio.html
  python -m igkit.cli mediakit --email me@example.com --out media_kit.md
  python -m igkit.cli deals add --brand Acme --fee 1500
  python -m igkit.cli deals list
"""

from __future__ import annotations

import argparse
import json
import sys

from igkit.config import Config


def _content(args, cfg: Config) -> int:
    from igkit.content import BrandProfile, ContentGenerator

    brand = BrandProfile.load(args.brand)
    gen = ContentGenerator(brand, config=cfg)
    if args.content_cmd == "captions":
        pkg = gen.generate_captions(args.topic, n=args.n)
        print(json.dumps(pkg.model_dump(), indent=2, ensure_ascii=False))
    elif args.content_cmd == "ideas":
        ideas = gen.generate_ideas(args.theme, n=args.n)
        print(json.dumps(ideas.model_dump(), indent=2, ensure_ascii=False))
    return 0


def _graph(cfg: Config):
    from igkit.graph import InstagramGraphClient

    token, user_id = cfg.require_graph()
    return InstagramGraphClient(token, user_id, version=cfg.ig_graph_version)


def _schedule(args, cfg: Config) -> int:
    from igkit.scheduler import ScheduleStore, run_due

    store = ScheduleStore(cfg.db_path)
    if args.schedule_cmd == "add":
        pid = store.enqueue(
            args.at, args.type, list(args.media), args.caption or ""
        )
        print(f"queued post #{pid} for {args.at}")
    elif args.schedule_cmd == "list":
        for p in store.list_all():
            print(
                f"#{p.id} {p.scheduled_at} {p.media_type} [{p.status}] "
                f"{p.caption[:40]!r}"
                + (f" err={p.error}" if p.error else "")
            )
    elif args.schedule_cmd == "run":
        summary = run_due(store, _graph(cfg))
        print(json.dumps(summary, indent=2))
    store.close()
    return 0


def _links(args, cfg: Config) -> int:
    from igkit.monetization import (
        LinkRegistry,
        build_utm_url,
        render_link_in_bio,
    )

    if args.links_cmd == "utm":
        print(
            build_utm_url(
                args.url, campaign=args.campaign, content=args.content
            )
        )
        return 0

    reg = LinkRegistry(cfg.db_path)
    if args.links_cmd == "add":
        link = reg.add_link(
            args.slug,
            args.url,
            link_type=args.type,
            campaign=args.campaign,
            title=args.title,
        )
        print(f"{link.slug} -> {link.destination}")
    elif args.links_cmd == "list":
        for l in reg.list_links():
            print(f"{l.slug} [{l.link_type}] clicks={l.clicks} -> {l.destination}")
    elif args.links_cmd == "bio":
        html_doc = render_link_in_bio(reg.export_bio(), page_title=args.title or "Links")
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(html_doc)
        print(f"wrote {args.out}")
    reg.close()
    return 0


def _mediakit(args, cfg: Config) -> int:
    from igkit.monetization import build_media_kit

    rate_card = json.loads(args.rates) if args.rates else None
    md = build_media_kit(
        _graph(cfg),
        contact_email=args.email,
        rate_card=rate_card,
        highlights=args.highlight or None,
    )
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(md)
        print(f"wrote {args.out}")
    else:
        print(md)
    return 0


def _deals(args, cfg: Config) -> int:
    from igkit.monetization import DealStore

    store = DealStore(cfg.db_path)
    if args.deals_cmd == "add":
        did = store.add(
            args.brand,
            contact=args.contact,
            fee=args.fee,
            deliverables=args.deliverables,
            due_date=args.due,
        )
        print(f"added deal #{did}")
    elif args.deals_cmd == "stage":
        store.set_stage(args.id, args.to)
        print(f"deal #{args.id} -> {args.to}")
    elif args.deals_cmd == "list":
        for d in store.list_all():
            print(
                f"#{d.id} {d.brand} [{d.stage}] "
                f"fee={d.fee or '-'} due={d.due_date or '-'}"
            )
        print("pipeline:", json.dumps(store.pipeline_value()))
    store.close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="igkit", description="Instagram automation toolkit")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("content", help="AI content generation")
    csub = c.add_subparsers(dest="content_cmd", required=True)
    cc = csub.add_parser("captions")
    cc.add_argument("--brand", required=True)
    cc.add_argument("--topic", required=True)
    cc.add_argument("--n", type=int, default=3)
    ci = csub.add_parser("ideas")
    ci.add_argument("--brand", required=True)
    ci.add_argument("--theme", required=True)
    ci.add_argument("--n", type=int, default=5)

    s = sub.add_parser("schedule", help="post scheduling")
    ssub = s.add_subparsers(dest="schedule_cmd", required=True)
    sa = ssub.add_parser("add")
    sa.add_argument("--at", required=True, help="ISO 8601, e.g. 2026-05-20T09:00:00+00:00")
    sa.add_argument("--type", required=True, choices=["image", "reel", "carousel"])
    sa.add_argument("--media", required=True, nargs="+", help="public media URL(s)")
    sa.add_argument("--caption", default="")
    ssub.add_parser("list")
    ssub.add_parser("run")

    l = sub.add_parser("links", help="affiliate / product links")
    lsub = l.add_subparsers(dest="links_cmd", required=True)
    la = lsub.add_parser("add")
    la.add_argument("--slug", required=True)
    la.add_argument("--url", required=True)
    la.add_argument(
        "--type", default="other",
        choices=["affiliate", "product", "content", "other"],
    )
    la.add_argument("--campaign")
    la.add_argument("--title")
    lu = lsub.add_parser("utm")
    lu.add_argument("--url", required=True)
    lu.add_argument("--campaign")
    lu.add_argument("--content")
    lsub.add_parser("list")
    lb = lsub.add_parser("bio")
    lb.add_argument("--out", default="bio.html")
    lb.add_argument("--title")

    m = sub.add_parser("mediakit", help="brand-deal media kit")
    m.add_argument("--email", required=True)
    m.add_argument("--out")
    m.add_argument("--rates", help='JSON map, e.g. \'{"1 Reel":"$800"}\'')
    m.add_argument("--highlight", action="append")

    d = sub.add_parser("deals", help="sponsorship pipeline")
    dsub = d.add_subparsers(dest="deals_cmd", required=True)
    da = dsub.add_parser("add")
    da.add_argument("--brand", required=True)
    da.add_argument("--contact")
    da.add_argument("--fee", type=float)
    da.add_argument("--deliverables")
    da.add_argument("--due")
    ds = dsub.add_parser("stage")
    ds.add_argument("--id", type=int, required=True)
    ds.add_argument("--to", required=True)
    dsub.add_parser("list")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cfg = Config.from_env()
    try:
        if args.cmd == "content":
            return _content(args, cfg)
        if args.cmd == "schedule":
            return _schedule(args, cfg)
        if args.cmd == "links":
            return _links(args, cfg)
        if args.cmd == "mediakit":
            return _mediakit(args, cfg)
        if args.cmd == "deals":
            return _deals(args, cfg)
    except (RuntimeError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
