#!/usr/bin/env python3
"""Build a formatted HTML + PDF job estimate from a normalized JSON file.

Usage:
    python3 build_estimate.py estimate.json [--out-dir DIR] [--no-html] [--no-pdf]

Input JSON must match ../schema.json. Money fields (subtotal, tax_amount,
total, and each line item's total) are recomputed from quantity/unit_cost/
tax_rate/discount rather than trusted from the input, so arithmetic is
always correct even if the JSON was hand-assembled.
"""
import argparse
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent


def load_and_validate(path: Path) -> dict:
    data = json.loads(path.read_text())
    try:
        import jsonschema
        schema = json.loads((SKILL_DIR / "schema.json").read_text())
        jsonschema.validate(data, schema)
    except ImportError:
        print("warning: jsonschema not installed, skipping schema validation", file=sys.stderr)
    return data


def compute_totals(data: dict) -> dict:
    subtotal = 0.0
    for item in data["line_items"]:
        item_total = round(item["quantity"] * item["unit_cost"], 2)
        item["total"] = item_total
        subtotal += item_total
    subtotal = round(subtotal, 2)

    discount = round(data.get("discount", 0) or 0, 2)
    taxable = max(subtotal - discount, 0)
    tax_rate = data.get("tax_rate", 0) or 0
    tax_amount = round(taxable * tax_rate / 100, 2)
    total = round(taxable + tax_amount, 2)

    data["subtotal"] = subtotal
    data["discount"] = discount
    data["tax_amount"] = tax_amount
    data["total"] = total
    return data


def money(value: float) -> str:
    return f"${value:,.2f}"


def render_html(data: dict, out_path: Path) -> None:
    from jinja2 import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader(str(SKILL_DIR / "templates")))
    env.filters["money"] = money
    template = env.get_template("estimate.html.j2")
    out_path.write_text(template.render(**data))


def render_pdf(data: dict, out_path: Path) -> None:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("EstTitle", parent=styles["Title"], fontSize=20, spaceAfter=4)
    meta_style = ParagraphStyle("EstMeta", parent=styles["Normal"], textColor=colors.grey)
    h2_style = ParagraphStyle("EstH2", parent=styles["Heading2"], spaceBefore=14, spaceAfter=6)
    body_style = styles["Normal"]

    story = []
    business = data.get("business", {}) or {}
    client = data["client"]
    job = data["job"]

    story.append(Paragraph(business.get("name", "Estimate"), title_style))
    biz_line = " | ".join(v for v in (business.get("phone"), business.get("email"), business.get("address")) if v)
    if biz_line:
        story.append(Paragraph(biz_line, meta_style))
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph(f"Estimate #{data['estimate_number']}", h2_style))
    meta_rows = [
        ["Date:", data["date"]],
        ["Valid until:", data.get("valid_until", "—")],
    ]
    meta_table = Table(meta_rows, colWidths=[1.2 * inch, 3 * inch])
    meta_table.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 9)]))
    story.append(meta_table)
    story.append(Spacer(1, 0.15 * inch))

    client_lines = [client["name"]]
    client_lines += [v for v in (client.get("address"), client.get("phone"), client.get("email")) if v]
    job_lines = [job["title"]]
    if job.get("location"):
        job_lines.append(job["location"])

    info_table = Table(
        [
            [Paragraph("<b>Client</b>", body_style), Paragraph("<b>Job</b>", body_style)],
            [Paragraph("<br/>".join(client_lines), body_style), Paragraph("<br/>".join(job_lines), body_style)],
        ],
        colWidths=[3 * inch, 3 * inch],
    )
    info_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(info_table)

    if job.get("description"):
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph(job["description"], body_style))

    story.append(Paragraph("Line Items", h2_style))
    header = ["Description", "Category", "Qty", "Unit", "Unit Cost", "Total"]
    rows = [header]
    for item in data["line_items"]:
        rows.append(
            [
                Paragraph(item["description"], body_style),
                item["category"],
                f"{item['quantity']:g}",
                item["unit"],
                money(item["unit_cost"]),
                money(item["total"]),
            ]
        )
    items_table = Table(rows, colWidths=[2.3 * inch, 0.9 * inch, 0.5 * inch, 0.6 * inch, 0.85 * inch, 0.85 * inch], repeatRows=1)
    items_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
            ]
        )
    )
    story.append(items_table)
    story.append(Spacer(1, 0.15 * inch))

    totals_rows = [["Subtotal", money(data["subtotal"])]]
    if data.get("discount"):
        totals_rows.append(["Discount", f"-{money(data['discount'])}"])
    if data.get("tax_rate"):
        totals_rows.append([f"Tax ({data['tax_rate']:g}%)", money(data["tax_amount"])])
    totals_rows.append(["Total", money(data["total"])])
    totals_table = Table(totals_rows, colWidths=[1.5 * inch, 1.1 * inch], hAlign="RIGHT")
    totals_table.setStyle(
        TableStyle(
            [
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ]
        )
    )
    story.append(totals_table)

    if data.get("notes"):
        story.append(Paragraph("Notes", h2_style))
        story.append(Paragraph(data["notes"], body_style))
    if data.get("terms"):
        story.append(Paragraph("Terms", h2_style))
        story.append(Paragraph(data["terms"], body_style))

    doc = SimpleDocTemplate(str(out_path), pagesize=letter, topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    doc.build(story)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Path to estimate JSON matching schema.json")
    parser.add_argument("--out-dir", type=Path, default=None, help="Output directory (default: alongside input)")
    parser.add_argument("--no-html", action="store_true")
    parser.add_argument("--no-pdf", action="store_true")
    args = parser.parse_args()

    data = load_and_validate(args.input)
    data = compute_totals(data)

    out_dir = args.out_dir or args.input.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = data["estimate_number"].replace("/", "-")

    normalized_path = out_dir / f"{stem}.json"
    normalized_path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"wrote {normalized_path}")

    if not args.no_html:
        html_path = out_dir / f"{stem}.html"
        render_html(data, html_path)
        print(f"wrote {html_path}")

    if not args.no_pdf:
        pdf_path = out_dir / f"{stem}.pdf"
        render_pdf(data, pdf_path)
        print(f"wrote {pdf_path}")


if __name__ == "__main__":
    main()
