# src/export/pdf_test_plan_exporter.py
# Generates a professional, styled PDF test plan using ReportLab

from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate
import re

import config

# ── Color Palette ─────────────────────────────────────────────
DEEP_BLUE    = colors.HexColor("#0d1f3c")
MID_BLUE     = colors.HexColor("#1a3a6b")
ACCENT_BLUE  = colors.HexColor("#2563eb")
LIGHT_BLUE   = colors.HexColor("#dbeafe")
CYAN         = colors.HexColor("#06b6d4")
WHITE        = colors.white
LIGHT_GREY   = colors.HexColor("#f1f5f9")
MID_GREY     = colors.HexColor("#94a3b8")
DARK_GREY    = colors.HexColor("#334155")
RED_HIGH     = colors.HexColor("#dc2626")
ORANGE_MED   = colors.HexColor("#ea580c")
GREEN_LOW    = colors.HexColor("#16a34a")
YELLOW_BG    = colors.HexColor("#fef9c3")
RED_BG       = colors.HexColor("#fee2e2")
GREEN_BG     = colors.HexColor("#dcfce7")


def build_styles():
    """Build all paragraph styles."""
    styles = getSampleStyleSheet()

    custom = {
        "DocTitle": ParagraphStyle("DocTitle",
            fontName="Helvetica-Bold", fontSize=26,
            textColor=WHITE, alignment=TA_CENTER,
            spaceAfter=6, leading=32),

        "DocSubtitle": ParagraphStyle("DocSubtitle",
            fontName="Helvetica", fontSize=12,
            textColor=colors.HexColor("#bfdbfe"),
            alignment=TA_CENTER, spaceAfter=4),

        "DocMeta": ParagraphStyle("DocMeta",
            fontName="Helvetica", fontSize=10,
            textColor=colors.HexColor("#93c5fd"),
            alignment=TA_CENTER, spaceAfter=2),

        "H1": ParagraphStyle("H1",
            fontName="Helvetica-Bold", fontSize=14,
            textColor=WHITE, backColor=DEEP_BLUE,
            spaceBefore=16, spaceAfter=8,
            leftIndent=0, rightIndent=0,
            borderPad=8, leading=20),

        "H2": ParagraphStyle("H2",
            fontName="Helvetica-Bold", fontSize=11,
            textColor=DEEP_BLUE, spaceBefore=12,
            spaceAfter=6, borderPadding=(0,0,2,0),
            leading=16),

        "H3": ParagraphStyle("H3",
            fontName="Helvetica-Bold", fontSize=10,
            textColor=MID_BLUE, spaceBefore=8,
            spaceAfter=4, leading=14),

        "Body": ParagraphStyle("Body",
            fontName="Helvetica", fontSize=9,
            textColor=DARK_GREY, spaceAfter=4,
            leading=14, leftIndent=0),

        "Bullet": ParagraphStyle("Bullet",
            fontName="Helvetica", fontSize=9,
            textColor=DARK_GREY, spaceAfter=3,
            leading=13, leftIndent=16,
            bulletIndent=6),

        "TableHeader": ParagraphStyle("TableHeader",
            fontName="Helvetica-Bold", fontSize=9,
            textColor=WHITE, alignment=TA_CENTER,
            leading=12),

        "TableCell": ParagraphStyle("TableCell",
            fontName="Helvetica", fontSize=9,
            textColor=DARK_GREY, leading=12,
            spaceAfter=2),

        "TableCellBold": ParagraphStyle("TableCellBold",
            fontName="Helvetica-Bold", fontSize=9,
            textColor=DARK_GREY, leading=12),

        "Priority_High": ParagraphStyle("Priority_High",
            fontName="Helvetica-Bold", fontSize=9,
            textColor=RED_HIGH, leading=12),

        "Priority_Med": ParagraphStyle("Priority_Med",
            fontName="Helvetica-Bold", fontSize=9,
            textColor=ORANGE_MED, leading=12),

        "Priority_Low": ParagraphStyle("Priority_Low",
            fontName="Helvetica-Bold", fontSize=9,
            textColor=GREEN_LOW, leading=12),

        "TOCItem": ParagraphStyle("TOCItem",
            fontName="Helvetica", fontSize=10,
            textColor=ACCENT_BLUE, spaceAfter=4,
            leading=14, leftIndent=8),

        "Footer": ParagraphStyle("Footer",
            fontName="Helvetica", fontSize=8,
            textColor=MID_GREY, alignment=TA_CENTER),

        "Code": ParagraphStyle("Code",
            fontName="Courier", fontSize=8,
            textColor=DARK_GREY, backColor=LIGHT_GREY,
            leading=12, leftIndent=8, spaceAfter=4),
    }
    return custom


def header_footer(canvas, doc):
    """Draw header and footer on every page."""
    canvas.saveState()
    w, h = A4

    # Header bar (skip cover page)
    if doc.page > 1:
        canvas.setFillColor(DEEP_BLUE)
        canvas.rect(0, h - 1.2*cm, w, 1.2*cm, fill=1, stroke=0)
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(1*cm, h - 0.8*cm, "QA ASSISTANT — TEST PLAN")
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(w - 1*cm, h - 0.8*cm,
            f"Generated: {datetime.now().strftime('%d %b %Y')}")

        # Footer
        canvas.setFillColor(LIGHT_GREY)
        canvas.rect(0, 0, w, 0.8*cm, fill=1, stroke=0)
        canvas.setFillColor(MID_GREY)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(1*cm, 0.3*cm, "BRAC IT Services — Internal QA Document")
        canvas.drawRightString(w - 1*cm, 0.3*cm, f"Page {doc.page}")

    canvas.restoreState()


def make_section_header(text: str, styles: dict):
    """Create a styled section header."""
    return [
        Spacer(1, 0.3*cm),
        Table([[Paragraph(text, styles["H1"])]],
            colWidths=[17*cm],
            style=TableStyle([
                ("BACKGROUND", (0,0), (-1,-1), DEEP_BLUE),
                ("TOPPADDING", (0,0), (-1,-1), 8),
                ("BOTTOMPADDING", (0,0), (-1,-1), 8),
                ("LEFTPADDING", (0,0), (-1,-1), 12),
                ("RIGHTPADDING", (0,0), (-1,-1), 12),
            ])
        ),
        Spacer(1, 0.2*cm),
    ]


def make_info_table(data: list, styles: dict, col_widths=None):
    """Create a styled 2-column info table."""
    if not col_widths:
        col_widths = [5*cm, 12*cm]
    table_data = []
    for key, val in data:
        table_data.append([
            Paragraph(key, styles["TableCellBold"]),
            Paragraph(str(val), styles["TableCell"]),
        ])
    t = Table(table_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), LIGHT_BLUE),
        ("BACKGROUND", (1,0), (1,-1), WHITE),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [LIGHT_GREY, WHITE]),
    ]))
    return t


def make_risk_table(risks: list, styles: dict):
    """Create a styled risk register table."""
    headers = ["Risk", "Impact", "Likelihood", "Mitigation"]
    header_row = [Paragraph(h, styles["TableHeader"]) for h in headers]
    rows = [header_row]

    for risk in risks:
        impact = risk.get("impact", "MED")
        style_key = "Priority_High" if impact == "HIGH" else \
                    "Priority_Med" if impact == "MED" else "Priority_Low"
        rows.append([
            Paragraph(risk.get("risk", ""), styles["TableCell"]),
            Paragraph(impact, styles[style_key]),
            Paragraph(risk.get("likelihood", "MED"), styles["TableCell"]),
            Paragraph(risk.get("mitigation", ""), styles["TableCell"]),
        ])

    t = Table(rows, colWidths=[5.5*cm, 2*cm, 2.5*cm, 7*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DEEP_BLUE),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LIGHT_GREY]),
    ]))
    return t


def make_checklist_table(items: list, styles: dict):
    """Create a QA release checklist table."""
    headers = ["☐", "Check Item", "Priority"]
    header_row = [Paragraph(h, styles["TableHeader"]) for h in headers]
    rows = [header_row]

    for item in items:
        priority = item.get("priority", "HIGH")
        style_key = "Priority_High" if priority == "CRITICAL" else \
                    "Priority_Med" if priority == "HIGH" else "Priority_Low"
        rows.append([
            Paragraph("☐", styles["TableCell"]),
            Paragraph(item.get("item", ""), styles["TableCell"]),
            Paragraph(priority, styles[style_key]),
        ])

    t = Table(rows, colWidths=[1*cm, 13*cm, 3*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DEEP_BLUE),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LIGHT_GREY]),
    ]))
    return t


def parse_test_plan_text(text: str) -> dict:
    """
    Parse LLM-generated test plan text into structured sections.
    Returns dict with section names as keys.
    """
    sections = {
        "document_control": [],
        "introduction": [],
        "scope_in": [],
        "scope_out": [],
        "test_levels": [],
        "tools": [],
        "features": [],
        "resources": [],
        "risks": [],
        "scenarios": [],
        "test_cases": [],
        "checklist": [],
        "exit_criteria": [],
        "raw": text
    }

    current_section = "introduction"
    lines = text.split("\n")

    for line in lines:
        line_lower = line.lower().strip()

        if any(k in line_lower for k in ["in scope", "in-scope"]):
            current_section = "scope_in"
        elif any(k in line_lower for k in ["out of scope", "out-of-scope"]):
            current_section = "scope_out"
        elif any(k in line_lower for k in ["risk register", "risk"]):
            current_section = "risks"
        elif any(k in line_lower for k in ["test level", "test type", "strategy"]):
            current_section = "test_levels"
        elif any(k in line_lower for k in ["feature", "to be tested"]):
            current_section = "features"
        elif any(k in line_lower for k in ["resource", "environment"]):
            current_section = "resources"
        elif any(k in line_lower for k in ["checklist", "release check"]):
            current_section = "checklist"
        elif any(k in line_lower for k in ["exit criteria", "suspension"]):
            current_section = "exit_criteria"
        elif any(k in line_lower for k in ["test case", "tc-"]):
            current_section = "test_cases"
        elif any(k in line_lower for k in ["scenario"]):
            current_section = "scenarios"
        elif any(k in line_lower for k in ["tool"]):
            current_section = "tools"

        if line.strip():
            sections[current_section].append(line)

    return sections


def generate_test_plan_pdf(
    test_plan_text: str,
    cr_id: str = "CR-001",
    cr_title: str = "Test Plan",
    author: str = "Senior QA Engineer",
    version: str = "1.0.0",
    filename: str = None
) -> Path:
    """
    Generate a professional PDF test plan from LLM-generated text.
    Returns path to the saved PDF file.
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"TestPlan_{cr_id}_{timestamp}.pdf"

    output_path = config.EXPORTS_PATH / filename
    styles = build_styles()

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm,
        topMargin=1.8*cm,
        bottomMargin=1.5*cm,
        title=f"Test Plan — {cr_id}",
        author=author,
        subject="QA Test Plan Document",
    )

    story = []
    w, h = A4

    # ── Cover Page ─────────────────────────────────────────────
    story.append(Spacer(1, 2*cm))

    # Cover header box
    cover_data = [[
        Paragraph("BRAC IT SERVICES", styles["DocMeta"]),
    ]]
    cover_top = Table(cover_data, colWidths=[17*cm])
    cover_top.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), CYAN),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(cover_top)

    # Main cover block
    cover_main = Table([[
        Paragraph("TEST PLAN", styles["DocTitle"]),
    ]], colWidths=[17*cm])
    cover_main.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DEEP_BLUE),
        ("TOPPADDING", (0,0), (-1,-1), 30),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(cover_main)

    cover_sub = Table([[
        Paragraph(cr_id, styles["DocSubtitle"]),
    ], [
        Paragraph(cr_title[:80], styles["DocSubtitle"]),
    ]], colWidths=[17*cm])
    cover_sub.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), MID_BLUE),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(cover_sub)

    cover_meta = Table([[
        Paragraph(f"Version {version}  |  {datetime.now().strftime('%B %Y')}  |  {author}",
                  styles["DocMeta"]),
    ]], colWidths=[17*cm])
    cover_meta.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DEEP_BLUE),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 30),
    ]))
    story.append(cover_meta)
    story.append(Spacer(1, 1*cm))

    # ── Document Control ──────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    dc_data = [
        ["CR / JIRA ID", cr_id],
        ["Test Plan Version", version],
        ["Prepared By", author],
        ["Generated On", datetime.now().strftime("%d %B %Y, %H:%M")],
        ["System Under Test", "BRAC Microfinance ERP"],
        ["Target Projects", "Progoti & ADP"],
    ]
    story.append(make_info_table(dc_data, styles))
    story.append(PageBreak())

    # ── Table of Contents ─────────────────────────────────────
    story += make_section_header("TABLE OF CONTENTS", styles)
    toc_items = [
        "1. Scope & Objectives",
        "2. Risk Register",
        "3. Test Strategy",
        "4. Key Test Scenarios",
        "5. Critical Test Cases",
        "6. Validation Layers",
        "7. Non-Functional Test Checks",
        "8. Test Data & Environment",
        "9. QA Release Checklist",
    ]
    for item in toc_items:
        story.append(Paragraph(f"• {item}", styles["TOCItem"]))
    story.append(PageBreak())

    # ── Parse and render the LLM content ─────────────────────
    sections = parse_test_plan_text(test_plan_text)

    # Render full text in structured sections
    current_h1 = None
    current_h2 = None
    in_table_block = False
    table_rows = []
    tc_blocks = []
    current_tc = []

    lines = test_plan_text.split("\n")

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_tc:
                tc_blocks.append(current_tc[:])
                current_tc = []
            story.append(Spacer(1, 0.15*cm))
            continue

        # H1 — "## 1. SCOPE"
        if stripped.startswith("## "):
            text = stripped.replace("## ", "").replace("#", "").strip()
            story += make_section_header(text, styles)
            continue

        # H2 — "### 1.1"
        if stripped.startswith("### "):
            text = stripped.replace("### ", "").replace("#", "").strip()
            story.append(Paragraph(text, styles["H2"]))
            continue

        # H3 — "#### "
        if stripped.startswith("#### "):
            text = stripped.replace("#### ", "").replace("#", "").strip()
            story.append(Paragraph(text, styles["H3"]))
            continue

        # Bold line (TC title, priority markers)
        if stripped.startswith("**") and stripped.endswith("**"):
            text = stripped.strip("*").strip()
            if "CRITICAL" in text or "HIGH" in text:
                story.append(Paragraph(text, styles["Priority_High"] if "CRITICAL" in text else styles["Priority_Med"]))
            else:
                story.append(Paragraph(f"<b>{text}</b>", styles["Body"]))
            continue

        # Table row
        if stripped.startswith("|") and stripped.endswith("|"):
            if "---" not in stripped:
                cells = [c.strip() for c in stripped.strip("|").split("|")]
                table_rows.append(cells)
            continue
        else:
            if table_rows:
                # Render collected table
                if len(table_rows) > 1:
                    num_cols = len(table_rows[0])
                    col_w = 17*cm / num_cols
                    t_data = []
                    for i, row in enumerate(table_rows):
                        if i == 0:
                            t_data.append([Paragraph(c, styles["TableHeader"]) for c in row])
                        else:
                            t_data.append([Paragraph(c, styles["TableCell"]) for c in row])
                    t = Table(t_data, colWidths=[col_w]*num_cols)
                    t.setStyle(TableStyle([
                        ("BACKGROUND", (0,0), (-1,0), DEEP_BLUE),
                        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                        ("VALIGN", (0,0), (-1,-1), "TOP"),
                        ("TOPPADDING", (0,0), (-1,-1), 6),
                        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
                        ("LEFTPADDING", (0,0), (-1,-1), 6),
                        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LIGHT_GREY]),
                    ]))
                    story.append(t)
                    story.append(Spacer(1, 0.2*cm))
                table_rows = []

        # Bullet point
        if stripped.startswith("- ") or stripped.startswith("• "):
            text = stripped.lstrip("-•").strip()
            # Color priority items
            if text.upper().startswith("HIGH") or "CRITICAL" in text.upper():
                story.append(Paragraph(f"• {text}", styles["Priority_High"]))
            elif text.upper().startswith("MED") or "MEDIUM" in text.upper():
                story.append(Paragraph(f"• {text}", styles["Priority_Med"]))
            else:
                story.append(Paragraph(f"• {text}", styles["Bullet"]))
            continue

        # Numbered list
        if len(stripped) > 2 and stripped[0].isdigit() and stripped[1] in ".):":
            story.append(Paragraph(stripped, styles["Bullet"]))
            continue

        # Regular body text
        story.append(Paragraph(stripped, styles["Body"]))

    # ── Footer note ───────────────────────────────────────────
    story.append(PageBreak())
    story += make_section_header("DOCUMENT END", styles)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "All CRITICAL items must be signed off before any production deployment. "
        "This document was auto-generated by QA Assistant powered by Llama 3.",
        styles["Body"]
    ))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=DEEP_BLUE))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%d %B %Y %H:%M')} | "
        f"Version: {version} | Author: {author}",
        styles["Footer"]
    ))

    # Build
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    return output_path