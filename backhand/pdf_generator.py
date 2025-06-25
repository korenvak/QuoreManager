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


def create_professional_pdf(customer_data, items_df, calculations, settings_manager, quote_id, save_path, demo1=None, demo2=None, visualization_images=None, technical_images=None):
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

    def process_image_for_pdf(img_path):
        """Process image: rotate landscape to portrait, optimize for PDF"""
        try:
            img = PILImage.open(img_path)
            
            # Check if image is landscape (width > height)
            if img.width > img.height:
                # Rotate landscape to portrait
                img = img.rotate(90, expand=True)
                logger.info(f"Rotated landscape image to portrait: {img_path}")
            
            # Optimize image size for PDF (max 1920x1080 to keep file size reasonable)
            max_width, max_height = 1920, 1080
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), PILImage.Resampling.LANCZOS)
                logger.info(f"Resized image for PDF optimization: {img_path}")
            
            return img
        except Exception as e:
            logger.error(f"Error processing image {img_path}: {e}")
            return None

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
    
    # Count image pages (backward compatibility + new system)
    if demo1: pages_total += 1
    if demo2: pages_total += 1
    if visualization_images:
        pages_total += len(visualization_images)
    if technical_images:
        pages_total += len(technical_images)
    
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

    # Prepare enhanced data for ReportLab Table with unit-aware formatting
    def format_quantity_with_unit(row):
        """Format quantity with proper unit display"""
        quantity = row.get('כמות', 0)
        unit = row.get('יחידה', '')
        
        # Format quantity based on unit type
        if unit == 'יח׳':
            # Integer quantities for pieces
            qty_text = f"{int(quantity)}"
        elif unit in ['מ"א', 'מ"ר']:
            # Float quantities for meters, show decimals only if needed
            if quantity == int(quantity):
                qty_text = f"{int(quantity)}"
            else:
                qty_text = f"{quantity:.2f}".rstrip('0').rstrip('.')
        else:
            # Other units or no unit
            if quantity == int(quantity):
                qty_text = f"{int(quantity)}"
            else:
                qty_text = f"{quantity:.2f}".rstrip('0').rstrip('.')
        
        # Add unit if it exists and item is not unitless
        if unit and unit.strip():
            return f"{qty_text} {unit}"
        else:
            # For unitless items, don't show quantity in PDF (they are fixed cost)
            return "1"
    
    def format_price(price):
        """Format price consistently"""
        return f"₪{price:,.2f}"
    
    def format_total(quantity, price):
        """Calculate and format total"""
        total = quantity * price
        return f"₪{total:,.2f}"
    
    # Process items with enhanced formatting
    processed_data = []
    for _, row in items_df.iterrows():
        # Debug logging for item processing
        logger.debug(f"Processing item: {row.get('שם מוצר', '')} - Price: {row.get('מחיר', 0)} - Unit: {row.get('יחידה', '')} - Quantity: {row.get('כמות', 0)}")
        
        # Format item name (truncate if too long)
        item_name = str(row.get('שם מוצר', ''))
        if len(item_name) > 50:
            item_name = item_name[:47] + "..."
        
        # Format quantity with unit
        qty_display = format_quantity_with_unit(row)
        
        # Format price - handle custom pricing (0 price items)
        price = row.get('מחיר', 0)
        if price == 0:
            price_display = "מחיר מותאם"
        else:
            price_display = format_price(price)
        
        # Format total - handle custom pricing
        if price == 0:
            total_display = ""  # Leave empty for manual cost items
        else:
            total_display = format_total(row.get('כמות', 0), price)
        
        processed_data.append([item_name, qty_display, price_display, total_display])
        logger.debug(f"Added to PDF: {item_name} | {qty_display} | {price_display} | {total_display}")
    
    # Create table headers
    headers = [rtl(h) for h in ["סה\"כ", "מחיר יחידה", "כמות", "שם הפריט"]]
    
    # Convert data to RTL format
    data_rtl = []
    for row in processed_data:
        rtl_row = [rtl(str(cell)) for cell in row]
        data_rtl.append(rtl_row[::-1])  # Reverse for RTL
    
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
    
    def add_image_page(img_path, title="תמונה"):
        """Add a single image page with title"""
        nonlocal page_num
        try:
            if not img_path or not os.path.exists(img_path):
                return
                
            c.showPage()
            page_num += 1
            draw_header(c)
            draw_watermark(c)
            
            # Add title
            c.setFillColorRGB(0, 0, 0)
            draw_rtl(c, W - m, H - 65*mm, title, PDF_BOLD, 16)
            
            # Process image (handle landscape, resize)
            processed_img = process_image_for_pdf(img_path)
            if processed_img:
                # Convert PIL image to temporary file for ReportLab
                temp_buffer = BytesIO()
                processed_img.save(temp_buffer, format='PNG')
                temp_buffer.seek(0)
                
                img_reader = ImageReader(temp_buffer)
                img_w, img_h = processed_img.size
                
                available_width = W - 2 * m
                available_height = H - 100*mm  # Leave space for title and footer
                
                scale_w = available_width / img_w
                scale_h = available_height / img_h
                scale = min(scale_w, scale_h)
                
                new_w = img_w * scale
                new_h = img_h * scale
                
                x_pos = (W - new_w) / 2
                y_pos = (H - new_h) / 2 - 30*mm  # Adjusted for title
                
                c.drawImage(img_reader, x_pos, y_pos, width=new_w, height=new_h, preserveAspectRatio=True, mask='auto')
            else:
                # Fallback to original method
                img_reader = ImageReader(img_path)
                img_w, img_h = img_reader.getSize()
                available_width = W - 2 * m
                available_height = H - 100*mm
                scale_w = available_width / img_w
                scale_h = available_height / img_h
                scale = min(scale_w, scale_h)
                new_w = img_w * scale
                new_h = img_h * scale
                x_pos = (W - new_w) / 2
                y_pos = (H - new_h) / 2 - 30*mm
                c.drawImage(img_reader, x_pos, y_pos, width=new_w, height=new_h, preserveAspectRatio=True, mask='auto')
            
            draw_footer(c, page_num, pages_total)
            
        except Exception as e:
            logger.error(f"Could not process image {img_path}: {e}")
    
    # Backward compatibility: Handle old demo1, demo2 parameters
    if demo1:
        add_image_page(demo1, "הדמיה")
    if demo2:
        add_image_page(demo2, "הדמיה")
    
    # New categorized image system
    if visualization_images:
        for img_path in visualization_images:
            add_image_page(img_path, "הדמיה")
    
    if technical_images:
        for img_path in technical_images:
            add_image_page(img_path, "הדמיית נקודות מים וחשמל")
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
            "הצעת המחיר תקפה ל־14 ימים ממועד הפקתה.\n\n"
            "ההצעה מיועדת ללקוח הספציפי בלבד, ואין להעבירה או להציג אותה בפני חברות אחרות או גורמים חיצוניים.\n\n"
            "המחירים עשויים להשתנות, והחברה אינה אחראית לטעויות חישוב או הקלדה. רק הסכום המאושר סופית על ידי החברה הוא המחייב.\n\n"
            "אישור ההצעה (בחתימה) מהווה התחייבות מצד הלקוח לביצוע העבודה.\n\n"
            "במעמד האישור, ישולמו 10% מקדמה מסכום העסקה – תשלום זה אינו ניתן להחזר במקרה של ביטול מכל סיבה שהיא.\n\n"
            "הלקוח מתחייב לוודא כי מיקום התקנת המטבח יהיה פנוי מכל ריהוט, ציוד או מכשול אחר, וכן שנקודות מים, חשמל וניקוז ימוקמו בהתאם לתכניות שסופקו לו מראש על ידי החברה.\n"
            "כל עיכוב או שינוי הנובע מאי־עמידה בתנאים אלה עשוי לגרור עיכובים בעלויות ולוחות זמנים."
        )
    legal_text = legal_text.replace('\\n', '\n')
    c.setFont(PDF_FONT, 10)
    lines = legal_text.split('\n')
    
    line_height = 6 * mm
    
    def wrap_text(text, font, font_size, max_width):
        """Wrap text to fit within max_width"""
        if not text.strip():
            return ['']
        
        c.setFont(font, font_size)
        words = text.split()
        lines = []
        current_line = ''
        
        for word in words:
            test_line = current_line + (' ' if current_line else '') + word
            test_line_rtl = rtl(test_line)
            text_width = c.stringWidth(test_line_rtl, font, font_size)
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
                # Check if single word is too long
                if c.stringWidth(rtl(word), font, font_size) > max_width:
                    # Word is too long, we'll have to let it overflow
                    pass
        
        if current_line:
            lines.append(current_line)
        
        return lines if lines else ['']
    
    # Calculate maximum text width (page width minus margins)
    max_text_width = W - 2 * m - 10 * mm  # Extra margin for safety
    
    for line in lines:
        # Wrap long lines
        wrapped_lines = wrap_text(line, PDF_FONT, 10, max_text_width)
        
        for wrapped_line in wrapped_lines:
            # Check if we have enough space for this line plus signature area
            if text_y - line_height < 50 * mm:  # Need space for signature (40mm) + footer (12mm)
                # Need a new page
                draw_footer(c, page_num, pages_total)
                c.showPage()
                page_num += 1
                draw_header(c)
                draw_watermark(c)
                c.setFillColorRGB(0, 0, 0)
                text_y = H - 60*mm
                # Add continuation header on new page
                draw_rtl(c, W - m, text_y, "תנאים והגבלות (המשך)", PDF_BOLD, 16)
                text_y -= 15*mm
                c.setFont(PDF_FONT, 10)
            
            if wrapped_line.strip():  # Only draw non-empty lines
                processed_line = rtl(wrapped_line)
                c.drawRightString(W - m, text_y, processed_line)
            text_y -= line_height
    
    # Draw signature line with adequate spacing
    sig_y = text_y - 30*mm
    if sig_y < 30*mm:  # Too close to bottom, need new page
        draw_footer(c, page_num, pages_total)
        c.showPage()
        page_num += 1
        draw_header(c)
        draw_watermark(c)
        c.setFillColorRGB(0, 0, 0)
        sig_y = H - 100*mm  # Place signature higher on new page
    
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