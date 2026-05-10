import io
import qrcode
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String
import datetime


def generate_qr_code(participant):
    """Generate QR code for participant and save to model."""
    url = f"/certificate/{participant.certificate_hash}/"
    qr = qrcode.QRCode(version=2, box_size=8, border=3,
                        error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1a1a2e", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    filename = f"qr_{participant.student_id}.png"
    participant.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)


def generate_certificate_pdf(participant):
    """Generate a styled PDF certificate using ReportLab."""
    buffer = io.BytesIO()

    # Page setup - landscape A4
    page_w, page_h = landscape(A4)
    c = canvas.Canvas(buffer, pagesize=landscape(A4))

    # --- Background gradient effect (solid with border) ---
    c.setFillColorRGB(0.98, 0.97, 0.94)  # warm cream
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    # Outer decorative border
    c.setStrokeColorRGB(0.6, 0.47, 0.18)  # gold
    c.setLineWidth(8)
    c.rect(20, 20, page_w - 40, page_h - 40, fill=0, stroke=1)

    # Inner border
    c.setStrokeColorRGB(0.8, 0.67, 0.3)
    c.setLineWidth(2)
    c.rect(30, 30, page_w - 60, page_h - 60, fill=0, stroke=1)

    # Corner ornaments
    for x, y in [(40, 40), (page_w - 40, 40), (40, page_h - 40), (page_w - 40, page_h - 40)]:
        c.setFillColorRGB(0.6, 0.47, 0.18)
        c.circle(x, y, 6, fill=1, stroke=0)

    # Header strip
    c.setFillColorRGB(0.08, 0.08, 0.2)  # deep navy
    c.rect(20, page_h - 95, page_w - 40, 55, fill=1, stroke=0)

    # Institution name
    c.setFillColorRGB(0.95, 0.82, 0.4)  # gold text
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(page_w / 2, page_h - 55, "ACADEMIC EVENT MANAGEMENT SYSTEM")
    c.setFillColorRGB(0.8, 0.72, 0.55)
    c.setFont("Helvetica", 9)
    c.drawCentredString(page_w / 2, page_h - 72, "Department of Computer Science & Engineering")

    # Certificate title
    c.setFillColorRGB(0.08, 0.08, 0.2)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(page_w / 2, page_h - 148, "CERTIFICATE")
    c.setFont("Helvetica", 14)
    c.setFillColorRGB(0.45, 0.35, 0.12)
    c.drawCentredString(page_w / 2, page_h - 170, "OF  PARTICIPATION")

    # Decorative line
    c.setStrokeColorRGB(0.6, 0.47, 0.18)
    c.setLineWidth(1.5)
    c.line(page_w / 2 - 120, page_h - 182, page_w / 2 + 120, page_h - 182)

    # Body text
    c.setFillColorRGB(0.25, 0.25, 0.25)
    c.setFont("Helvetica", 12)
    c.drawCentredString(page_w / 2, page_h - 210, "This is to certify that")

    # Participant name
    c.setFillColorRGB(0.05, 0.1, 0.35)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(page_w / 2, page_h - 245, participant.name.upper())

    # Underline for name
    name_width = c.stringWidth(participant.name.upper(), "Helvetica-Bold", 28)
    c.setStrokeColorRGB(0.6, 0.47, 0.18)
    c.setLineWidth(1)
    c.line(page_w / 2 - name_width / 2, page_h - 252,
           page_w / 2 + name_width / 2, page_h - 252)

    # Student ID
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.setFont("Helvetica", 10)
    c.drawCentredString(page_w / 2, page_h - 267, f"Student ID: {participant.student_id}")

    # Body continued
    c.setFillColorRGB(0.25, 0.25, 0.25)
    c.setFont("Helvetica", 12)
    c.drawCentredString(page_w / 2, page_h - 290,
                        "has successfully participated in the event")

    # Event name
    c.setFillColorRGB(0.05, 0.1, 0.35)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(page_w / 2, page_h - 315, f'"{participant.event.name}"')

    # Date and venue
    c.setFillColorRGB(0.3, 0.3, 0.3)
    c.setFont("Helvetica", 11)
    date_str = participant.event.date.strftime("%B %d, %Y")
    c.drawCentredString(page_w / 2, page_h - 338,
                        f"Held on {date_str}  ·  {participant.event.venue}")

    # Footer strip
    c.setFillColorRGB(0.08, 0.08, 0.2)
    c.rect(20, 20, page_w - 40, 70, fill=1, stroke=0)

    # Signature lines
    sig_y = 68
    for sx, label in [(130, "Event Coordinator"), (page_w / 2, "Head of Department"),
                      (page_w - 130, "Principal")]:
        c.setStrokeColorRGB(0.9, 0.78, 0.45)
        c.setLineWidth(1)
        c.line(sx - 60, sig_y + 20, sx + 60, sig_y + 20)
        c.setFillColorRGB(0.85, 0.75, 0.5)
        c.setFont("Helvetica", 8)
        c.drawCentredString(sx, sig_y + 8, label)

    # Certificate hash (verification)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.setFont("Helvetica", 7)
    c.drawCentredString(page_w / 2, 30, f"Verify at: /certificate/{participant.certificate_hash}/  |  Issued: {datetime.date.today()}")

    # Attendance verified badge (top right)
    c.setFillColorRGB(0.12, 0.55, 0.22)
    c.roundRect(page_w - 165, page_h - 190, 130, 30, 5, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(page_w - 100, page_h - 170, "✓ ATTENDANCE VERIFIED")

    c.setFillColorRGB(0.12, 0.45, 0.65)
    c.roundRect(page_w - 165, page_h - 228, 130, 30, 5, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(page_w - 100, page_h - 208, "✓ FEEDBACK SUBMITTED")

    c.save()
    buffer.seek(0)
    return buffer
