import io
import json
import datetime
from decimal import Decimal, InvalidOperation

from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

from . import utils


# ---------------------------------------------------------------------------
# Bills
# ---------------------------------------------------------------------------

@login_required
def bills(request, uuid):
    """GET    → list bills in category folder
       POST   → upload a new bill image to Drive
       DELETE → delete one or more bills by filename"""

    if request.method == 'GET':
        bill_list = utils.list_of_bills(request, [uuid])
        return JsonResponse({'bills': bill_list})

    if request.method == 'POST':
        image = request.FILES.get('image')
        value_raw = request.POST.get('value')

        if not image or value_raw is None:
            return JsonResponse({'error': 'image and value are required'}, status=400)

        try:
            value = Decimal(value_raw)
        except InvalidOperation:
            return JsonResponse({'error': 'Invalid value'}, status=400)

        creds, creds_data, service = utils.create_service(request)
        if service is None:
            return JsonResponse({'error': 'Drive service unavailable'}, status=503)

        folder_id = utils.return_folder_id(service)
        cat_name = utils.return_cat_name(request, uuid)
        cat_id = utils.return_folder_id(service, folder_id, [cat_name])
        formatted_name = utils.image_name(request, uuid, value)
        utils.upload_image_to_drive(service, image, formatted_name, image.content_type, cat_id)
        utils.randomizer(request)
        return JsonResponse({'ok': True, 'name': formatted_name}, status=201)

    if request.method == 'DELETE':
        try:
            body = json.loads(request.body)
            names = body.get('names', [])
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        if not names:
            return JsonResponse({'error': 'No bills specified'}, status=400)
        creds, creds_data, service = utils.create_service(request)
        if service is None:
            return JsonResponse({'error': 'Drive service unavailable'}, status=503)
        deleted = 0
        for name in names:
            file_id = utils.get_image_id(service, name)
            if file_id:
                utils.delete_file(service, file_id)
                deleted += 1
        return JsonResponse({'ok': True, 'deleted': deleted})

    return JsonResponse({'error': 'Method not allowed'}, status=405)


# ---------------------------------------------------------------------------
# Single bill (view / rename value)
# ---------------------------------------------------------------------------

@login_required
def bill(request):
    """GET   → resolve filename and return Drive image id + metadata
       PATCH → rename file (change value field)"""

    date = request.GET.get('date')
    time = request.GET.get('time')
    category = request.GET.get('category')
    value_raw = request.GET.get('value')

    if not all([date, time, category, value_raw]):
        return JsonResponse({'error': 'date, time, category and value query params required'}, status=400)

    try:
        value = Decimal(value_raw)
    except InvalidOperation:
        return JsonResponse({'error': 'Invalid value'}, status=400)

    value_name = '{:012.2f}'.format(value)
    name = f'{category}_{date}_{time}_{value_name}'

    creds, creds_data, service = utils.create_service(request)
    if service is None:
        return JsonResponse({'error': 'Drive service unavailable'}, status=503)

    if request.method == 'GET':
        file_id = utils.get_image_id(service, name)
        return JsonResponse({
            'id': file_id,
            'name': name,
            'value': str(value),
            'date': date,
            'time': time,
            'category': category,
        })

    if request.method == 'PATCH':
        try:
            body = json.loads(request.body)
            new_value = Decimal(str(body.get('value', '')))
        except (json.JSONDecodeError, AttributeError, InvalidOperation):
            return JsonResponse({'error': 'Invalid JSON or value'}, status=400)

        file_id = utils.get_image_id(service, name)
        if not file_id:
            return JsonResponse({'error': 'Bill not found'}, status=404)

        new_value_name = '{:012.2f}'.format(new_value)
        new_name = f'{category}_{date}_{time}_{new_value_name}'
        utils.rename_folder(service, file_id, new_name)
        return JsonResponse({'ok': True, 'name': new_name, 'id': file_id})

    return JsonResponse({'error': 'Method not allowed'}, status=405)


# ---------------------------------------------------------------------------
# Clean edit (delete old image + upload new one)
# ---------------------------------------------------------------------------

@login_required
def clean_edit_bill(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    date = request.GET.get('date')
    time_val = request.GET.get('time')
    category = request.GET.get('category')
    value_raw = request.GET.get('value')

    if not all([date, time_val, category, value_raw]):
        return JsonResponse({'error': 'date, time, category and value query params required'}, status=400)

    try:
        value = Decimal(value_raw)
    except InvalidOperation:
        return JsonResponse({'error': 'Invalid value'}, status=400)

    value_name = '{:012.2f}'.format(value)
    old_name = f'{category}_{date}_{time_val}_{value_name}'

    new_value_raw = request.POST.get('value', value_raw)
    new_category = request.POST.get('category', category)
    keep_old = request.POST.get('keep_old', 'false').lower() == 'true'
    new_image = request.FILES.get('image')

    try:
        new_value = Decimal(new_value_raw)
    except InvalidOperation:
        return JsonResponse({'error': 'Invalid new value'}, status=400)

    new_value_name = '{:012.2f}'.format(new_value)
    new_name = f'{new_category}_{date}_{time_val}_{new_value_name}'

    creds, creds_data, service = utils.create_service(request)
    if service is None:
        return JsonResponse({'error': 'Drive service unavailable'}, status=503)

    folder_id = utils.return_folder_id(service)

    if new_image:
        # Capture the old file's ID before uploading, so a same-name new file
        # doesn't make get_image_id ambiguous.
        old_id = utils.get_image_id(service, old_name) if not keep_old else None
        new_cat_id = utils.return_folder_id(service, folder_id, [new_category])
        uploaded = utils.upload_image_to_drive(service, new_image, new_name, new_image.content_type, new_cat_id)
        if old_id:
            utils.delete_file(service, old_id)
        return JsonResponse({'ok': True, 'id': uploaded['id'], 'name': new_name})

    else:
        # No new image — rename and/or move the existing Drive file
        if old_name == new_name:
            return JsonResponse({'ok': True, 'name': old_name})
        old_id = utils.get_image_id(service, old_name)
        if not old_id:
            return JsonResponse({'error': 'Bill not found'}, status=404)
        if new_category != category:
            old_cat_id = utils.return_folder_id(service, folder_id, [category])
            new_cat_id = utils.return_folder_id(service, folder_id, [new_category])
            service.files().update(
                fileId=old_id,
                body={'name': new_name},
                addParents=new_cat_id,
                removeParents=old_cat_id,
                fields='id, parents'
            ).execute()
        else:
            utils.rename_folder(service, old_id, new_name)
        return JsonResponse({'ok': True, 'name': new_name})


# ---------------------------------------------------------------------------
# Export — multi-category or single
# ---------------------------------------------------------------------------

@login_required
def export(request, uuid=None):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    start_str = body.get('start_date')
    end_str = body.get('end_date')

    if not start_str or not end_str:
        return JsonResponse({'error': 'start_date and end_date required'}, status=400)

    try:
        start_date = datetime.date.fromisoformat(start_str)
        end_date = datetime.date.fromisoformat(end_str)
    except ValueError:
        return JsonResponse({'error': 'Dates must be ISO format YYYY-MM-DD'}, status=400)

    if uuid is None:
        categories = body.get('categories', [])
        if not categories:
            return JsonResponse({'error': 'categories list required'}, status=400)
        uuid_list = utils.names_to_uuid(request, categories)
    else:
        uuid_list = [uuid]

    bill_list = utils.list_of_bills(request, uuid_list, start_date, end_date)
    request.session['Final_bills'] = bill_list
    utils.randomizer(request)
    return JsonResponse({'bills': bill_list, 'count': len(bill_list)})


# ---------------------------------------------------------------------------
# PDF download
# ---------------------------------------------------------------------------

@login_required
def export_pdf(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    data_rows = utils.table_data(request)

    # ── Colours matching the light UI theme ──────────────────────────────────
    INDIGO_DARK = colors.HexColor('#1a237e')
    INDIGO_MID  = colors.HexColor('#3949ab')
    BG_LIGHT    = colors.HexColor('#eef2fb')
    BG_WHITE    = colors.HexColor('#ffffff')
    GREEN_DARK  = colors.HexColor('#2e7d32')
    GRID_COLOR  = colors.HexColor('#c5d5f5')
    TOTAL_BG    = colors.HexColor('#dce8fb')

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=28,
        rightMargin=28,
        topMargin=36,
        bottomMargin=36,
    )

    # ── Title block ──────────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        'title',
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=INDIGO_DARK,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    sub_style = ParagraphStyle(
        'sub',
        fontName='Helvetica',
        fontSize=9,
        textColor=INDIGO_MID,
        alignment=TA_CENTER,
        spaceAfter=16,
    )
    today = datetime.date.today().strftime('%d %B %Y')
    elements = [
        Paragraph('DocWallet — Bill Export', title_style),
        Paragraph(f'Generated on {today}', sub_style),
        Spacer(1, 6),
    ]

    # ── Table ────────────────────────────────────────────────────────────────
    header = ['Date', 'Time', 'Category', 'Value (£)']
    data = [header] + data_rows
    n = len(data)
    last = n - 1  # index of the TOTAL row

    page_width = A4[0] - doc.leftMargin - doc.rightMargin
    total_units = 2 + 2 + 5 + 3
    unit = page_width / total_units
    col_widths = [unit * 2, unit * 2, unit * 5, unit * 3]

    table = Table(data, colWidths=col_widths, repeatRows=1)

    style_cmds = [
        # Layout
        ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',    (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
        # Grid
        ('GRID',          (0, 0), (-1, -1), 0.5, GRID_COLOR),
        ('LINEBELOW',     (0, 0), (-1, 0),  1.2, INDIGO_DARK),
        # Header row
        ('BACKGROUND',    (0, 0), (-1, 0),  INDIGO_DARK),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.white),
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, 0),  9),
        # Body rows
        ('FONTNAME',      (0, 1), (-1, last - 1), 'Helvetica'),
        ('FONTSIZE',      (0, 1), (-1, last - 1), 9),
        ('TEXTCOLOR',     (0, 1), (-1, last - 1), INDIGO_DARK),
        # Value column (col 3) — dark green, bold
        ('TEXTCOLOR',     (3, 1), (3, last - 1), GREEN_DARK),
        ('FONTNAME',      (3, 1), (3, last - 1), 'Helvetica-Bold'),
        # Total row
        ('BACKGROUND',    (0, last), (-1, last), TOTAL_BG),
        ('TEXTCOLOR',     (0, last), (-1, last), INDIGO_DARK),
        ('FONTNAME',      (0, last), (-1, last), 'Helvetica-Bold'),
        ('FONTSIZE',      (0, last), (-1, last), 9),
        ('LINEABOVE',     (0, last), (-1, last), 1.2, INDIGO_MID),
    ]

    # Alternating row backgrounds for body rows
    for i in range(1, last):
        bg = BG_WHITE if i % 2 == 0 else BG_LIGHT
        style_cmds.append(('BACKGROUND', (0, i), (-1, i), bg))

    table.setStyle(TableStyle(style_cmds))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="DocWallet_Bills.pdf"'
    return response
