# file: panel_app/pdf_generator.py
import io
import os
import logging
from datetime import date, datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm
from PIL import Image as PILImage
from io import BytesIO
from reportlab.lib.colors import HexColor, Color
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from utils.helpers import asset_path
from utils.rtl import rtl

# Configure logging
logger = logging.getLogger(__name__)


def create_professional_pdf(customer_data, items_df, calculations, settings_manager, quote_id, save_path, demo1=None, demo2=None):
    """Create a modern, professional PDF quote and save it to the specified path."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    W, H = A4
    m = 20 * mm
    ROW_HEIGHT = 8 * mm

    try:
        reg_path = asset_path('Heebo-Regular.ttf')
        bold_path = asset_path('Heebo-Bold.ttf')
        if os.path.exists(reg_path) and os.path.exists(bold_path):
            pdfmetrics.registerFont(TTFont('Heebo', reg_path))
            pdfmetrics.registerFont(TTFont('Heebo-Bold', bold_path))
            PDF_FONT = 'Heebo'
            PDF_BOLD = 'Heebo-Bold'
        else:
            logger.warning("Heebo fonts not found, using fallback fonts")
            PDF_FONT = PDF_BOLD = 'Helvetica'
    except (OSError, IOError) as e:
        logger.error(f"Failed to load fonts: {e}")
        PDF_FONT = PDF_BOLD = 'Helvetica'
    except Exception as e:
        logger.error(f"Unexpected error loading fonts: {e}")
        PDF_FONT = PDF_BOLD = 'Helvetica'

    def draw_rtl(canv, x, y, text, font=PDF_FONT, fontsize=12):
        try:
            canv.setFont(font, fontsize)
            canv.drawRightString(x, y, rtl(text))
        except Exception as e:
            logger.error(f"Error drawing RTL text: {e}")
            canv.setFont('Helvetica', fontsize)
            canv.drawRightString(x, y, str(text))

    def draw_watermark(canv):
        wm_path = asset_path('watermark.png')
        if os.path.exists(wm_path):
            try:
                canv.saveState()
                canv.setFillAlpha(0.05)
                img = ImageReader(wm_path)
                w_img, h_img = img.getSize()
                scale = min((W / 2) / w_img, (H / 2) / h_img)
                nw, nh = w_img * scale, h_img * scale
                canv.translate(W / 2, H / 2)
                canv.rotate(45)
                canv.drawImage(img, -nw / 2, -nh / 2, width=nw, height=nh, mask='auto')
                canv.restoreState()
            except Exception as e:
                logger.error(f"Error drawing watermark: {e}")

    def draw_footer(canv, page, total):
        canv.setFillColorRGB(0.827, 0.184, 0.184)
        canv.rect(0, 0, W, 3 * mm, fill=1, stroke=0)
        x = m
        logo_path = asset_path('logo.png')
        if os.path.exists(logo_path):
            try:
                img = ImageReader(logo_path)
                w, h = img.getSize()
                scale = (8 * mm) / h
                canv.drawImage(img, x, 4 * mm, height=8 * mm, width=w * scale, preserveAspectRatio=True, mask='auto')
                x += w * scale + 5 * mm
            except Exception as e:
                logger.error(f"Error drawing logo: {e}")
        canv.setFont(PDF_FONT, 9)
        canv.setFillColorRGB(0, 0, 0)
        company_details = settings_manager.get_company_info()
        info = f"{company_details.get('address', '')} | טל: {company_details.get('phone', '')} | דוא\"ל: {company_details.get('email', '')}"
        c.drawString(x, 7 * mm, rtl(info))
        page_text = rtl(f"עמוד {page} מתוך {total}")
        canv.setFont(PDF_FONT, 9)
        canv.drawRightString(W - m, 7 * mm, page_text)

    def draw_header(canv):
        canv.setFillColorRGB(0.98, 0.98, 0.98)
        canv.rect(0, H - 40 * mm, W, 40 * mm, fill=1, stroke=0)
        logo_big = asset_path('logo.png')
        logo_w = 60 * mm
        if os.path.exists(logo_big):
            try:
                img = ImageReader(logo_big)
                w_img, h_img = img.getSize()
                ratio = logo_w / w_img
                logo_h = h_img * ratio
                canv.drawImage(img, m, H - 25 * mm - logo_h / 2, width=logo_w, height=logo_h, preserveAspectRatio=True, mask='auto')
            except Exception as e:
                logger.error(f"Error drawing header logo: {e}")
        canv.setFont(PDF_BOLD, 42)
        canv.setFillColorRGB(0.827, 0.184, 0.184)
        draw_rtl(c, W - m, H - 28 * mm, 'הצעת מחיר')
        return H - 45 * mm

    # Calculate page count
    pages_total = 1
    num_items = len(items_df)
    items_per_first_page = 12
    items_per_page = 25
    if num_items > items_per_first_page:
        additional_pages = ((num_items - items_per_first_page) // items_per_page) + 1
        pages_total += additional_pages
    if demo1: pages_total += 1
    if demo2: pages_total += 1
    pages_total += 1 # Legal text page

    page_num = 1
    y = draw_header(c)
    draw_watermark(c)
    c.setFillColorRGB(0, 0, 0)

    # Customer info as a card
    card_x, card_y, card_w, card_h = m, y - 50*mm, W - 2*m, 45*mm
    c.roundRect(card_x, card_y, card_w, card_h, 10, stroke=1, fill=0)
    c.setFillColorRGB(0.1, 0.1, 0.1)
    date_str = customer_data.get('date', '')
    if date_str and isinstance(date_str, str):
        try:
            formatted_date = datetime.strptime(date_str.split('T')[0], '%Y-%m-%d').strftime('%d/%m/%Y')
        except (ValueError, TypeError):
            formatted_date = date_str
    elif isinstance(customer_data.get('date'), date):
        formatted_date = customer_data['date'].strftime('%d/%m/%Y')
    else:
        formatted_date = date.today().strftime('%d/%m/%Y')
    details_y = card_y + card_h - 12*mm
    details_x_right = card_x + card_w - 10*mm
    details_x_left = card_x + card_w / 2 - 10*mm
    draw_rtl(c, details_x_right, details_y, f"לכבוד: {customer_data.get('name', '')}", font=PDF_BOLD, fontsize=12)
    draw_rtl(c, details_x_right, details_y - 10*mm, f"תאריך: {formatted_date}", font=PDF_FONT, fontsize=10)
    draw_rtl(c, details_x_left, details_y, f"טלפון: {customer_data.get('phone', '')}", font=PDF_FONT, fontsize=10)
    draw_rtl(c, details_x_left, details_y - 10*mm, f"דוא\"ל: {customer_data.get('email', '')}", font=PDF_FONT, fontsize=10)
    draw_rtl(c, details_x_right, details_y - 20*mm, f"כתובת: {customer_data.get('address', '')}", font=PDF_FONT, fontsize=10)
    y = card_y - 10 * mm

    # Items Table
    y -= 15*mm

    # Prepare data for ReportLab Table - including headers
    items_df['total'] = items_df['כמות'] * items_df['מחיר']
    
    headers = [rtl(h) for h in ["סה\"כ", "מחיר", "כמות", "שם הפריט"]]
    data = items_df[['שם מוצר', 'כמות', 'מחיר', 'total']].values.tolist()
    data_rtl = [[rtl(str(cell)) for cell in row] for row in data]
    data_rtl = [row[::-1] for row in data_rtl]
    table_data = [headers] + data_rtl
    col_widths = [25*mm, 25*mm, 25*mm, W - (3*25*mm) - 2*m]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D43A3A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), PDF_BOLD),
        ('FONTNAME', (0, 1), (-1, -1), PDF_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 3*mm),
        ('TOPPADDING', (0, 0), (-1, 0), 3*mm),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 2*mm),
        ('TOPPADDING', (0, 1), (-1, -1), 2*mm),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DDDDDD')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    table.setStyle(style)
    while len(table_data) > 1:
        remaining_height = y - 90*mm
        rows_that_fit = 0
        for i in range(1, len(table_data) + 1):
            slice_to_check = Table(table_data[:i], colWidths=col_widths, repeatRows=1)
            slice_to_check.setStyle(style)
            if slice_to_check.wrapOn(c, 0, 0)[1] > remaining_height:
                break
            rows_that_fit = i
        if rows_that_fit <= 1 and len(table_data) > 1:
            c.showPage()
            page_num += 1
            draw_header(c)
            draw_watermark(c)
            draw_footer(c, page_num, pages_total)
            y = H - 60*mm
            if rows_that_fit == 0:
                continue
        fitted_table = Table(table_data[:rows_that_fit], colWidths=col_widths, repeatRows=1)
        fitted_table.setStyle(style)
        fitted_table_height = fitted_table.wrapOn(c, 0, 0)[1]
        fitted_table.drawOn(c, m, y - fitted_table_height)
        y -= (fitted_table_height + 10*mm)
        table_data = [table_data[0]] + table_data[rows_that_fit:]
        if len(table_data) > 1:
            c.showPage()
            page_num += 1
            draw_header(c)
            draw_watermark(c)
            draw_footer(c, page_num, pages_total)
            y = H - 60*mm
    if y < 100*mm:
        c.showPage()
        page_num += 1
        draw_header(c)
        draw_watermark(c)
        draw_footer(c, page_num, pages_total)
        y = H - 60*mm
    totals_card_x = W / 2
    totals_card_w = W / 2 - m
    num_rows = 3
    if calculations.get('contractor_discount_val', 0) > 0: num_rows += 1
    if calculations.get('discount_val', 0) > 0: num_rows += 1
    totals_card_h = (num_rows * 11*mm) + 15*mm
    totals_card_y = y - totals_card_h
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.roundRect(totals_card_x, totals_card_y, totals_card_w, totals_card_h, 10, stroke=1, fill=0)
    total_y = totals_card_y + totals_card_h - 12*mm
    def draw_total_row(label, value, is_bold=False, is_final=False):
        nonlocal total_y
        font = PDF_BOLD if is_bold else PDF_FONT
        fontsize = 13 if is_final else 11
        c.setFillColorRGB(0, 0, 0)
        draw_rtl(c, totals_card_x + totals_card_w - 10*mm, total_y, label, font, fontsize)
        value_text = f"₪{value:,.2f}"
        c.setFont(font, fontsize)
        c.drawString(totals_card_x + 10*mm, total_y, rtl(value_text))
        total_y -= (12*mm if is_final else 11*mm)
    draw_total_row("סכום ביניים:", calculations['subtotal'])
    if calculations.get('contractor_discount_val', 0) > 0:
        draw_total_row("הנחת קבלן:", -calculations['contractor_discount_val'])
    if calculations.get('discount_val', 0) > 0:
        draw_total_row(f"הנחה ({calculations['discount_percent']}%):", -calculations['discount_val'])
    vat_rate = settings_manager.get('vat_rate', 17.0)
    draw_total_row(f"מע\"מ ({vat_rate}%):", calculations['vat_amount'])
    total_y += 6*mm
    c.line(totals_card_x + 5*mm, total_y, totals_card_x + totals_card_w - 5*mm, total_y)
    total_y -= 7*mm
    draw_total_row("סה\"כ לתשלום:", calculations['final_total'], is_bold=True, is_final=True)
    draw_footer(c, page_num, pages_total)
    image_paths = [demo1, demo2]
    for img_path in image_paths:
        if img_path and os.path.exists(img_path):
            try:
                c.showPage()
                page_num += 1
                pages_total += 1
                draw_header(c)
                draw_watermark(c)
                img = PILImage.open(img_path)
                img_w, img_h = img.size
                available_width = W - 2 * m
                available_height = H - 80*mm
                scale_w = available_width / img_w
                scale_h = available_height / img_h
                scale = min(scale_w, scale_h)
                new_w = img_w * scale
                new_h = img_h * scale
                x_pos = (W - new_w) / 2
                y_pos = (H - new_h) / 2 - 20*mm
                c.drawImage(ImageReader(img_path), x_pos, y_pos, width=new_w, height=new_h, preserveAspectRatio=True, mask='auto')
                draw_footer(c, page_num, pages_total)
            except Exception as e:
                logger.error(f"Could not process image {img_path}: {e}")
    c.showPage()
    page_num += 1
    draw_header(c)
    draw_watermark(c)
    text_y = H - 60*mm
    c.setFillColorRGB(0, 0, 0)
    draw_rtl(c, W - m, text_y, "תנאים והגבלות", PDF_BOLD, 16)
    text_y -= 15*mm
    legal_text = settings_manager.get('legal_text', '')
    if not legal_text:
        legal_text = (
            "הצעת המחיר תקפה ל-14 ימים ממועד הפקתה.\n"
            "ההצעה מתייחסת לריהוט בלבד, ולא כוללת עבודות תשתית כגון חשמל, אינסטלציה וגז.\n"
            "כל שינוי או תוספת מהמצוין בהצעה יתומחרו בנפרד.\n"
            "אישור ההצעה מהווה הסכמה לתנאים ומחייב חתימת הלקוח ותשלום מקדמה של 10% מסכום ההצעה."
        )
    legal_text = legal_text.replace('\\n', '\n')
    c.setFont(PDF_FONT, 10)
    lines = legal_text.split('\n')
    for line in lines:
        processed_line = rtl(line)
        c.drawRightString(W - m, text_y, processed_line)
        text_y -= 6 * mm
    sig_y = text_y - 40*mm
    c.line(W - m - 80*mm, sig_y - 2*mm, W - m, sig_y - 2*mm)
    draw_rtl(c, W - m, sig_y, "חתימת הלקוח:")
    draw_footer(c, page_num, pages_total)
    c.save()
    buffer.seek(0)

    # --- UPDATED FILE SAVING LOGIC ---
    # The save_path is now provided as an argument.
    try:
        with open(save_path, 'wb') as f:
            f.write(buffer.getvalue())
        logger.info(f"Successfully saved PDF to {save_path}")
    except IOError as e:
        logger.error(f"Failed to save PDF to {save_path}: {e}")
        return None  # Return None on failure

    return save_path  # Return the path where it was saved

def create_enhanced_pdf(*args, **kwargs):
    """Fallback or alternative PDF function. Can be an older design."""
    return create_professional_pdf(*args, **kwargs)