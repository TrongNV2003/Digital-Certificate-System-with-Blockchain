import os
import requests
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing
from reportlab.lib.pagesizes import A4, landscape
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle


font_path = "backend/static/DejaVuSans.ttf"
pdfmetrics.registerFont(TTFont('DejaVu', font_path))

def get_logo_image():
    logo_path = "backend/static/hust.png"
    if os.path.exists(logo_path):
        return Image(logo_path, width=2 * inch, height=2 * inch)
    else:
        url = "https://www.python.org/static/community_logos/python-logo.png"
        r = requests.get(url)
        if r.status_code == 200:
            tmp_path = "backend/static/hust.png"
            with open(tmp_path, "wb") as f:
                f.write(r.content)
            img = Image(tmp_path, width=2 * inch, height=2 * inch)
            img.hAlign = 'CENTER'
            return img
        else:
            return None

def generate_certificate_pdf(cert_id: str, recipient: str, course: str, issue_date: str, tx_hash: str):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name='Title',
        fontName='DejaVu',
        fontSize=24,
        alignment=1,
        spaceAfter=20,
        textColor=colors.darkblue
    )
    content_style = ParagraphStyle(
        name='Content',
        fontName='DejaVu',
        fontSize=14,
        alignment=1,
        spaceAfter=12,
        leading=18
    )
    signature_style = ParagraphStyle(
        name='Signature',
        fontName='DejaVu',
        fontSize=12,
        alignment=1,
        spaceAfter=8
    )

    elements.append(Paragraph("Chứng Nhận Hoàn Thành", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    logo = get_logo_image()
    if logo:
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(f"Được cấp cho: <b>{recipient}</b>", content_style))
    elements.append(Paragraph(f"Đã hoàn thành khóa học: <b>{course}</b>", content_style))
    elements.append(Paragraph(f"Mã chứng chỉ: {cert_id}", content_style))
    elements.append(Paragraph(f"Ngày cấp: {issue_date}", content_style))
    elements.append(Spacer(1, 0.3 * inch))

    qr = QrCodeWidget(tx_hash)
    bounds = qr.getBounds()
    d = Drawing(100, 100)
    d.add(qr)

    signature_block = [
        Paragraph("Chữ ký số xác thực Blockchain", signature_style),
        Spacer(1, 0.05 * inch),
        Paragraph("<b>Nguyễn Văn Trọng</b>", signature_style),
        Paragraph("Giám đốc đào tạo", signature_style),
        Paragraph("Cơ quan cấp chứng chỉ", signature_style),
    ]

    table_data = [
        [d, '', signature_block]
    ]
    table = Table(table_data, colWidths=[2.2*inch, 4.5*inch, 3.5*inch])
    table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'CENTER'),
        ('ALIGN', (2,0), (2,0), 'RIGHT'),
        ('BOX', (0,0), (-1,-1), 0, colors.white),
        ('INNERGRID', (0,0), (-1,-1), 0, colors.white),
    ]))

    elements.append(table)

    doc.build(elements)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data

# if __name__ == "__main__":
#     pdf_data = generate_certificate_pdf(
#         cert_id="CERT123456",
#         recipient="Nguyen Van A",
#         course="Khóa học Python Nâng cao",
#         issue_date="01/01/2024",
#         tx_hash="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
#     )
#     with open("certificate_example.pdf", "wb") as f:
#         f.write(pdf_data)