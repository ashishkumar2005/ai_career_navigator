from __future__ import annotations

from io import BytesIO
import html
import re
import zlib


def build_pdf_report(title: str, profile: dict, recommendations: list[dict], insights: dict) -> bytes:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ModuleNotFoundError:
        return _build_simple_pdf(title, profile, recommendations, insights)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42)
    styles = getSampleStyleSheet()
    story = [Paragraph(title, styles["Title"]), Spacer(1, 14)]

    story.append(Paragraph("Profile Summary", styles["Heading2"]))
    for label, value in profile.items():
        if value and label != "resume_text":
            story.append(Paragraph(f"<b>{html.escape(label.title())}:</b> {html.escape(str(value))}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Recommended Careers", styles["Heading2"]))
    rows = [["Career", "Match", "Missing Skills"]]
    for rec in recommendations[:5]:
        rows.append([rec["career_role"], f"{rec['match_percentage']}%", ", ".join(rec["missing_skills"][:5]) or "None"])
    table = Table(rows, colWidths=[165, 75, 250])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#172033")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d6dbe7")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )
    story.extend([table, Spacer(1, 12)])

    story.append(Paragraph("Insights", styles["Heading2"]))
    for label, value in insights.items():
        story.append(Paragraph(f"<b>{html.escape(label.replace('_', ' ').title())}:</b> {html.escape(str(value))}", styles["BodyText"]))

    doc.build(story)
    return buffer.getvalue()


def _build_simple_pdf(title: str, profile: dict, recommendations: list[dict], insights: dict) -> bytes:
    lines = [title, "", "Profile Summary"]
    for key, value in profile.items():
        if value and key != "resume_text":
            lines.append(f"{key.replace('_', ' ').title()}: {value}")

    lines.extend(["", "Recommended Careers"])
    for rec in recommendations[:5]:
        missing = ", ".join(rec["missing_skills"][:5]) or "None"
        lines.append(f"{rec['career_role']} - {rec['match_percentage']}% match - Missing: {missing}")

    lines.extend(["", "Insights"])
    for key, value in insights.items():
        lines.append(f"{key.replace('_', ' ').title()}: {value}")

    return _minimal_pdf(lines)


def _minimal_pdf(lines: list[str]) -> bytes:
    safe_lines = []
    for line in lines:
        clean = re.sub(r"[^\x20-\x7E]", " ", str(line))
        safe_lines.append(clean[:115])

    content_lines = ["BT", "/F1 12 Tf", "50 760 Td", "16 TL"]
    for index, line in enumerate(safe_lines[:42]):
        if index:
            content_lines.append("T*")
        escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        content_lines.append(f"({escaped}) Tj")
    content_lines.append("ET")
    stream = "\n".join(content_lines).encode("latin-1", errors="ignore")
    compressed = zlib.compress(stream)

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(compressed)).encode() + b" /Filter /FlateDecode >>\nstream\n" + compressed + b"\nendstream",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode())
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())
    pdf.extend(f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode())
    return bytes(pdf)
