"""Generate PDF and DOCX exports for users / groups / banned-site lists."""
import os
import tempfile
from datetime import datetime
from typing import Sequence

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, Image as RLImage
)
from docx.shared import Inches

from app.models import Group, User, ForensicCase

_FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\segoeui.ttf",
)


def _find_font() -> str | None:
    for p in _FONT_CANDIDATES:
        if os.path.exists(p):
            return p
    return None


def _escape_html(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class ExportService:
    # ─── Users ───────────────────────────────────────
    def users_pdf(self, users: Sequence[User]) -> str:
        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        doc = SimpleDocTemplate(tmp.name, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = [
            Paragraph("<b>SafeGuard Bot — Foydalanuvchilar Ro'yxati</b>", styles["Title"]),
            Spacer(1, 12),
            Paragraph("Sana: " + datetime.now().strftime("%d.%m.%Y %H:%M"), styles["Normal"]),
            Spacer(1, 6),
            Paragraph(f"Jami: {len(users)} ta foydalanuvchi", styles["Normal"]),
            Spacer(1, 20),
        ]
        data = [["#", "Ism", "Username", "Telefon", "Telegram ID", "Sana"]]
        for i, u in enumerate(users, 1):
            data.append([str(i), u.first_name or "-", u.at_username if u.username else "-",
                         u.phone or "-", str(u.user_id), u.registered_at or "-"])

        table = Table(data, colWidths=[25, 80, 90, 100, 90, 90])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F2F2F2"), colors.white]),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(table)
        doc.build(elements)
        return tmp.name

    def users_docx(self, users: Sequence[User]) -> str:
        tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
        doc = Document()
        title = doc.add_heading("SafeGuard Bot — Foydalanuvchilar Ro'yxati", 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph("Sana: " + datetime.now().strftime("%d.%m.%Y %H:%M"))
        doc.add_paragraph(f"Jami: {len(users)} ta foydalanuvchi")
        doc.add_paragraph("")

        table = doc.add_table(rows=1, cols=6)
        table.style = "Table Grid"
        for i, h in enumerate(["#", "Ism", "Username", "Telefon", "Telegram ID", "Sana"]):
            cell = table.rows[0].cells[i]
            cell.text = h
            cell.paragraphs[0].runs[0].bold = True

        for i, u in enumerate(users, 1):
            row = table.add_row().cells
            row[0].text = str(i)
            row[1].text = u.first_name or "-"
            row[2].text = u.at_username if u.username else "-"
            row[3].text = u.phone or "-"
            row[4].text = str(u.user_id)
            row[5].text = u.registered_at or "-"

        doc.save(tmp.name)
        return tmp.name

    # ─── Groups ──────────────────────────────────────
    def groups_pdf(self, groups: Sequence[Group]) -> str:
        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        doc = SimpleDocTemplate(tmp.name, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = [
            Paragraph("<b>SafeGuard Bot — Guruhlar Ro'yxati</b>", styles["Title"]),
            Spacer(1, 10),
            Paragraph("Sana: " + datetime.now().strftime("%d.%m.%Y %H:%M"), styles["Normal"]),
            Paragraph(f"Jami: {len(groups)} ta guruh", styles["Normal"]),
            Spacer(1, 16),
        ]
        data = [["#", "Nomi", "Username", "Holat", "Qo'shilgan sana"]]
        for i, g in enumerate(groups, 1):
            data.append([
                str(i), g.title or "—", g.at_username,
                "Aktiv" if g.is_active else "Chiqarilgan", g.added_at or "—",
            ])

        table = Table(data, colWidths=[25, 120, 100, 80, 100])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f0f0f0"), colors.white]),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(table)
        doc.build(elements)
        return tmp.name

    def groups_docx(self, groups: Sequence[Group]) -> str:
        tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
        doc = Document()
        h = doc.add_heading("SafeGuard Bot — Guruhlar Ro'yxati", 0)
        h.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph("Sana: " + datetime.now().strftime("%d.%m.%Y %H:%M"))
        doc.add_paragraph(f"Jami: {len(groups)} ta guruh")
        doc.add_paragraph("")
        table = doc.add_table(rows=1, cols=5)
        table.style = "Table Grid"
        for i, h_text in enumerate(["#", "Nomi", "Username", "Holat", "Qo'shilgan sana"]):
            cell = table.rows[0].cells[i]
            cell.text = h_text
            cell.paragraphs[0].runs[0].bold = True
        for i, g in enumerate(groups, 1):
            row = table.add_row().cells
            row[0].text = str(i)
            row[1].text = g.title or "—"
            row[2].text = g.at_username
            row[3].text = "Aktiv" if g.is_active else "Chiqarilgan"
            row[4].text = g.added_at or "—"
        doc.save(tmp.name)
        return tmp.name

    # ─── Banned sites ────────────────────────────────
    def banned_pdf(self, title: str, items: Sequence[str], note: str) -> str:
        font_name = "Helvetica"
        font_path = _find_font()
        if font_path:
            try:
                pdfmetrics.registerFont(TTFont("UniFont", font_path))
                font_name = "UniFont"
            except Exception:
                pass

        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        doc = SimpleDocTemplate(tmp.name, pagesize=A4,
                                leftMargin=40, rightMargin=40,
                                topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("TitleUni", parent=styles["Title"],
                                     fontName=font_name, fontSize=14, spaceAfter=8)
        normal_style = ParagraphStyle("NormalUni", parent=styles["Normal"],
                                      fontName=font_name, fontSize=9, leading=13)
        item_style = ParagraphStyle("ItemUni", parent=styles["Normal"],
                                    fontName=font_name, fontSize=8, leading=11, leftIndent=4)

        elements = [
            Paragraph(f"<b>{_escape_html(title)}</b>", title_style),
            Spacer(1, 6),
            Paragraph("Sana: " + datetime.now().strftime("%d.%m.%Y %H:%M"), normal_style),
            Spacer(1, 10),
            HRFlowable(width="100%", thickness=1, color=colors.grey),
            Spacer(1, 8),
        ]
        for item in items:
            clean = item.replace("📌 ", "").replace("🚫 ", "")
            elements.append(Paragraph(f"• {_escape_html(clean)}", item_style))
            elements.append(Spacer(1, 3))

        elements.append(Spacer(1, 12))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        elements.append(Spacer(1, 6))
        if note:
            elements.append(Paragraph(f"<i>{_escape_html(note)}</i>", normal_style))

        doc.build(elements)
        return tmp.name

    def banned_docx(self, title: str, items: Sequence[str], note: str) -> str:
        tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
        doc = Document()
        h = doc.add_heading(title, 0)
        h.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph("Sana: " + datetime.now().strftime("%d.%m.%Y %H:%M"))
        doc.add_paragraph("")
        for item in items:
            clean = item.replace("📌 ", "").replace("🚫 ", "")
            doc.add_paragraph(clean, style="List Bullet")
        doc.add_paragraph("")
        if note:
            note_para = doc.add_paragraph(note)
            if note_para.runs:
                note_para.runs[0].italic = True
        doc.save(tmp.name)
        return tmp.name

    def forensic_report_pdf(self, case: ForensicCase) -> str:
        font_name = "Helvetica"
        font_path = _find_font()
        if font_path:
            try:
                pdfmetrics.registerFont(TTFont("UniFont", font_path))
                font_name = "UniFont"
            except Exception:
                pass

        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        doc = SimpleDocTemplate(tmp.name, pagesize=A4,
                                leftMargin=40, rightMargin=40,
                                topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            "GovTitle", parent=styles["Title"], fontName=font_name, fontSize=11, leading=14, spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            "GovSubtitle", parent=styles["Title"], fontName=font_name, fontSize=13, leading=16, spaceAfter=15
        )
        label_style = ParagraphStyle(
            "CaseLabel", parent=styles["Normal"], fontName=font_name + "-Bold" if font_path is None else font_name, 
            fontSize=10, leading=13
        )
        value_style = ParagraphStyle(
            "CaseValue", parent=styles["Normal"], fontName=font_name, fontSize=10, leading=13
        )
        text_style = ParagraphStyle(
            "CaseText", parent=styles["Normal"], fontName=font_name, fontSize=10, leading=14
        )

        elements = [
            Paragraph("<b>O'ZBEKISTON RESPUBLIKASI ICHKI ISHLAR VAZIRLIGI</b>", title_style),
            Paragraph("<b>KIBERXAVFSIZLIK DEPARTAMENTI VA RAQAMLI EKSPERTIZA XULOSASI</b>", subtitle_style),
            HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2C3E50")),
            Spacer(1, 10),
        ]

        details_data = [
            [Paragraph("<b>Hujjat raqami (ID):</b>", label_style), Paragraph(f"#{case.id}", value_style)],
            [Paragraph("<b>Sana va vaqt:</b>", label_style), Paragraph(case.detected_at, value_style)],
            [Paragraph("<b>Manzil (Guruh):</b>", label_style), Paragraph(f"{case.chat_title} (ID: {case.chat_id})", value_style)],
            [Paragraph("<b>Qonunbuzarlik turi:</b>", label_style), Paragraph(case.display_violation, value_style)],
            [Paragraph("<b>Huquqbuzar (Ism):</b>", label_style), Paragraph(case.full_name, value_style)],
            [Paragraph("<b>Username / ID:</b>", label_style), Paragraph(f"@{case.username if case.username else 'yo'q'} / ID: {case.user_id}", value_style)],
            [Paragraph("<b>Telefon raqam:</b>", label_style), Paragraph(case.phone if case.phone else "ulashilmagan", value_style)],
            [Paragraph("<b>Tizim xulosasi:</b>", label_style), Paragraph(case.reason, value_style)],
        ]

        if case.photo_path and os.path.exists(case.photo_path):
            try:
                img = RLImage(case.photo_path, width=110, height=110)
                t_details = Table(details_data, colWidths=[120, 250])
                t_details.setStyle(TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                ]))
                
                layout_table = Table([[t_details, img]], colWidths=[380, 130])
                layout_table.setStyle(TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (1, 0), (1, 0), "CENTER"),
                ]))
                elements.append(layout_table)
            except Exception:
                t_details = Table(details_data, colWidths=[130, 380])
                t_details.setStyle(TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]))
                elements.append(t_details)
        else:
            t_details = Table(details_data, colWidths=[130, 380])
            t_details.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            elements.append(t_details)

        elements.append(Spacer(1, 15))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        elements.append(Spacer(1, 10))

        elements.append(Paragraph("<b>ASLIY JINOYAT ASYOSI (DALIL MATNI):</b>", label_style))
        elements.append(Spacer(1, 5))
        
        msg_box_data = [[Paragraph(f'<i>"{_escape_html(case.message_text)}"</i>', text_style)]]
        msg_table = Table(msg_box_data, colWidths=[510])
        msg_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8F9FA")),
            ("PADDING", (0, 0), (-1, -1), 10),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
        ]))
        elements.append(msg_table)

        elements.append(Spacer(1, 20))
        
        legal_note = {
            "extremism": "Ushbu bayonnoma O'zbekiston Respublikasi JK 244-1-moddasi (Jamoat xavfsizligiga tahdid soluvchi materiallarni tarqatish) bo'yicha jinoiy ish qo'zg'atish uchun asos bo'la oladi.",
            "drugs": "Ushbu bayonnoma O'zbekiston Respublikasi JK 273-moddasi (Giyohvandlik moddalari savdosi va yashirin aylanmasi) bo'yicha jinoiy ish qo'zg'atish uchun asos bo'la oladi.",
            "bullying": "Ushbu bayonnoma O'zbekiston Respublikasi JK 140-moddasi (Haqorat qilish) hamda MJtK 41-moddasiga ko'ra dalil sifatida foydalanilishi mumkin."
        }.get(case.violation_type, "Ushbu hujjat kiber-ekspertiza dalili sifatida tergov organlariga taqdim etiladi.")

        elements.append(Paragraph(f"<b>Eslatma:</b> <i>{legal_note}</i>", value_style))
        elements.append(Spacer(1, 30))
        
        sig_data = [
            [Paragraph("<b>Mas'ul ekspert:</b>", value_style), Paragraph("________________________", value_style), Paragraph("(Imzo)", value_style)],
            [Paragraph("<b>Departament boshlig'i:</b>", value_style), Paragraph("________________________", value_style), Paragraph("(Imzo)", value_style)]
        ]
        sig_table = Table(sig_data, colWidths=[150, 200, 100])
        sig_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(sig_table)

        doc.build(elements)
        return tmp.name

    def forensic_report_docx(self, case: ForensicCase) -> str:
        tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
        doc = Document()
        
        h1 = doc.add_heading("O'ZBEKISTON RESPUBLIKASI ICHKI ISHLAR VAZIRLIGI", 1)
        h1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        h2 = doc.add_heading("KIBERXAVFSIZLIK DEPARTAMENTI VA RAQAMLI EKSPERTIZA XULOSASI", 2)
        h2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph("Sana: " + datetime.now().strftime("%d.%m.%Y %H:%M"))
        doc.add_paragraph(f"Bayonnoma ID: #{case.id}")
        doc.add_paragraph("-" * 80)
        
        table = doc.add_table(rows=0, cols=2)
        table.style = "Table Grid"
        
        def add_row(lbl, val):
            row_cells = table.add_row().cells
            row_cells[0].text = lbl
            row_cells[0].paragraphs[0].runs[0].bold = True
            row_cells[1].text = str(val)

        add_row("Tergov ID raqami:", f"#{case.id}")
        add_row("Sana va vaqt:", case.detected_at)
        add_row("Manzil (Guruh):", f"{case.chat_title} (ID: {case.chat_id})")
        add_row("Qonunbuzarlik turi:", case.display_violation)
        add_row("Huquqbuzar ismi:", case.full_name)
        add_row("Username / Telegram ID:", f"@{case.username if case.username else 'yo\'q'} / ID: {case.user_id}")
        add_row("Telefon raqami:", case.phone if case.phone else "ulashilmagan")
        add_row("Tizim tahlili sababi:", case.reason)
        
        doc.add_paragraph("")
        
        if case.photo_path and os.path.exists(case.photo_path):
            try:
                doc.add_paragraph("Huquqbuzar Telegram profil rasmi (Dalil):")
                doc.add_picture(case.photo_path, width=Inches(2.0))
                doc.add_paragraph("")
            except Exception:
                pass
                
        doc.add_heading("ASLIY JINOYAT ASYOSI (DALIL MATNI)", 3)
        evidence_para = doc.add_paragraph()
        evidence_para.paragraph_format.left_indent = Inches(0.5)
        run = evidence_para.add_run(f'"{case.message_text}"')
        run.italic = True
        
        doc.add_paragraph("")
        doc.add_paragraph("-" * 80)
        
        legal_note = {
            "extremism": "Ushbu bayonnoma O'zbekiston Respublikasi JK 244-1-moddasi bo'yicha jinoiy ish qo'zg'atish uchun asos bo'la oladi.",
            "drugs": "Ushbu bayonnoma O'zbekiston Respublikasi JK 273-moddasi bo'yicha jinoiy ish qo'zg'atish uchun asos bo'la oladi.",
            "bullying": "Ushbu bayonnoma O'zbekiston Respublikasi JK 140-moddasi hamda MJtK 41-moddasiga ko'ra dalil sifatida ishlatilishi mumkin."
        }.get(case.violation_type, "Kiber-ekspertiza dalil bayonnomasi.")
        
        doc.add_paragraph(f"Eslatma: {legal_note}")
        doc.add_paragraph("")
        doc.add_paragraph("Mas'ul ekspert: ________________________ (Imzo)")
        doc.add_paragraph("Departament boshlig'i: ________________________ (Imzo)")
        
        doc.save(tmp.name)
        return tmp.name
