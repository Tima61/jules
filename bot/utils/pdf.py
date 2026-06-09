import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
from bot.config import BASE_ADDRESS

# Register Cyrillic font
font_path = "bot/assets/DejaVuSans.ttf"
pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_path)) # We'll just use the regular as bold for simplicity if bold is missing, or register a proper bold if needed. Here we map both to the same file for robustness if the style requests Bold.

def generate_commercial_proposal(client_data: dict, map_image_path: str | None, distance: float | None) -> str:
    telegram_id = client_data.get('telegram_id', 'unknown')
    pdf_path = f"bot/assets/temp/proposal_{telegram_id}.pdf"
    os.makedirs("bot/assets/temp", exist_ok=True)

    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName='DejaVuSans',
        fontSize=20,
        spaceAfter=14
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName='DejaVuSans',
        fontSize=12,
        spaceAfter=10
    )

    bold_style = ParagraphStyle(
        'CustomBold',
        parent=styles['Normal'],
        fontName='DejaVuSans', # Or DejaVuSans-Bold if available
        fontSize=12,
        spaceAfter=10,
        textColor='black'
    )

    story = []

    # Header: Logo
    logo_path = "bot/assets/logo.png"
    if os.path.exists(logo_path):
        img = Image(logo_path, 2*inch, 2*inch)
        story.append(img)
        story.append(Spacer(1, 0.2*inch))

    # Title
    story.append(Paragraph("Коммерческое Предложение", title_style))
    story.append(Paragraph('От: Прачечная "ЧИСТЫЙ СТЕПАШКА"', normal_style))
    story.append(Paragraph(f'Наш адрес: {BASE_ADDRESS}', normal_style))
    story.append(Spacer(1, 0.2*inch))

    # Client Details
    story.append(Paragraph("<b>Детали вашего запроса:</b>", bold_style))
    story.append(Paragraph(f"Компания: {client_data.get('company_name')}", normal_style))
    story.append(Paragraph(f"Контактное лицо: {client_data.get('contact_person')}", normal_style))
    story.append(Paragraph(f"Тип текстиля: {client_data.get('textile_type')}", normal_style))
    story.append(Paragraph(f"Объем (кг/нед): {client_data.get('volume_kg')}", normal_style))
    story.append(Spacer(1, 0.2*inch))

    # Logistics
    if client_data.get('delivery_required'):
        story.append(Paragraph("<b>Логистика:</b>", bold_style))
        story.append(Paragraph(f"Адрес забора: {client_data.get('address')}", normal_style))

        if distance is not None:
            story.append(Paragraph(f"Расстояние от нашего производства: {distance:.2f} км", normal_style))

        if map_image_path and os.path.exists(map_image_path):
            story.append(Spacer(1, 0.2*inch))
            map_img = Image(map_image_path, width=5*inch, height=3.3*inch)
            story.append(map_img)
    else:
        story.append(Paragraph("<b>Логистика:</b> Доставка не требуется (самовывоз).", bold_style))

    doc.build(story)
    return pdf_path
