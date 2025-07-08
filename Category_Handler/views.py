import os,pytz,uuid,io,datetime
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests
from .Google import Create_Service
from django.contrib.auth.decorators import login_required
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from Login_Handler.models import GoogleCredentials,List_of_categories,User_Profile
from django.utils.timezone import make_aware, is_naive
from django.utils import timezone
from google.auth.transport.requests import Request
from . import utils
from .forms import ImageUploadForm,TimeframeForm,TimeframeForm_2,EditUploadForm,ImageUploadForm_2
from googleapiclient.http import MediaIoBaseUpload
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from decimal import Decimal

def inside_category(request,UUID):  
    list = utils.list_of_bills(request,[UUID])
    return render(request, 'bills_page.html', {'list':list,'uuid':UUID})

def add(request,UUID):
    if request.method == "POST":
        form = ImageUploadForm(request.POST,request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            value = form.cleaned_data['value']
            creds,creds_data,service = utils.create_service(request)
            folder_id = utils.return_folder_id(service)
            cat_id = utils.return_folder_id(service,folder_id,[utils.return_cat_name(request,UUID)])
            formatted_name = utils.image_name(request,UUID,value)
            utils.upload_image_to_drive(service,image,formatted_name,image.content_type,cat_id)
            utils.randomizer(request)
            return redirect('home')
    else:
        form = ImageUploadForm()
    return render(request, 'new_bill.html', {'form':form})

def export(request,UUID=None):
    if UUID is None:
        if request.method == "POST":
            form = TimeframeForm(request.POST, request=request)
            if form.is_valid():
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                categories = form.cleaned_data['categories']
                uuid_list = utils.names_to_uuid(request,categories)
                l = utils.list_of_bills(request,uuid_list,start_date,end_date)
                request.session['Final_bills']=l
                utils.randomizer(request)
                return render(request, 'chosen_bills.html', {'list':l,'length':len(l)})
        else:
            form = TimeframeForm(request=request)
        return render(request, 'select_timeframe.html', {'form': form})
    else:
        if request.method == "POST":
            form = TimeframeForm_2(request.POST)
            if form.is_valid():
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                categories = [utils.return_cat_name(request,UUID)]
                uuid_list = utils.names_to_uuid(request,categories)
                l = utils.list_of_bills(request,uuid_list,start_date,end_date)
                request.session['Final_bills']=l
                utils.randomizer(request)
                return render(request, 'chosen_bills.html', {'list':l,'length':len(l)})
        else:
            form = TimeframeForm_2()
        return render(request, 'select_timeframe.html', {'form': form})

def download(request,rows):
    try:
        row_count = int(rows)
    except ValueError:
        return HttpResponse("Invalid row count", status=400)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
    buffer,
    pagesize=A4,
    leftMargin=20,
    rightMargin=20,
    topMargin=40,
    bottomMargin=40,
    )
    elements = []

    header = ["Date", "Time", "Category", "Value"]

    data_rows = utils.table_data(request)
    data = [header] + data_rows
    print(data)
    page_width = A4[0] - doc.leftMargin - doc.rightMargin
    total_units = 2+2+5+3
    unit_width = page_width / total_units
    col_widths = [
    unit_width * 2,  # Column 1
    unit_width * 2,  # Column 2
    unit_width * 5,  # Column 3
    unit_width * 3,  # Column 4
]
    # Table + styling
    table = Table(data, colWidths=col_widths)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Bills.pdf"'
    return response

def view_bill(request):
    date = request.GET.get('date')
    time = request.GET.get('time')
    category = request.GET.get('category')
    value = Decimal(request.GET.get('value'))
    value_name = "{:012.2f}".format(value)
    name = category + '_' + date + '_' + time + '_' + value_name
    creds,creds_data,service = utils.create_service(request)
    id = utils.get_image_id(service,name)
    return render(request,'bill.html',{'id':id,'value':value,'name':name})

def edit_bill(request):
    date = request.GET.get('date')
    time = request.GET.get('time')
    category = request.GET.get('category')
    value = Decimal(request.GET.get('value'))
    value_name = "{:012.2f}".format(value)
    creds,creds_data,service = utils.create_service(request)
    name = category + '_' + date + '_' + time + '_' + value_name
    id = utils.get_image_id(service,name)
    if request.method == "POST":
        form = EditUploadForm(request.POST)
        if form.is_valid():
            value = form.cleaned_data['value']
            value_name = "{:012.2f}".format(value)
            name = category + '_' + date + '_' + time + '_' + value_name
            utils.rename_folder(service,id,name)
            return render(request,'bill.html',{'id':id,'value':value,'name':name})
    else:
        form = EditUploadForm(initial={'value': value})
    return render(request, 'new_bill_2.html', {'form':form,'name':name})

def clean_edit_bill(request):
    date = request.GET.get('date')
    time = request.GET.get('time')
    category = request.GET.get('category')
    value = Decimal(request.GET.get('value'))
    value_name = "{:012.2f}".format(value)
    creds,creds_data,service = utils.create_service(request)
    name = category + '_' + date + '_' + time + '_' + value_name
    if request.method == "POST":
        form = ImageUploadForm_2(data=request.POST, files=request.FILES, request=request)
        if form.is_valid():
            id = utils.get_image_id(service,name)
            image = form.cleaned_data['image']
            value = form.cleaned_data['value']
            category_choice = form.cleaned_data['category']
            value_name = "{:012.2f}".format(value)
            name = category_choice + '_' + date + '_' + time + '_' + value_name
            utils.delete_file(service,id)
            uuid = utils.names_to_uuid(request,[category_choice])
            parent_id = utils.return_folder_id(service)
            cat_name=utils.return_cat_name(request,uuid[0])
            cat_id = utils.return_folder_id(service,parent_id,[cat_name])
            id = utils.upload_image_to_drive(service,image,name,image.content_type,cat_id)
            print(id)
            return render(request,'bill.html',{'id':id['id'],'value':value,'name':name})
    else:
        form = ImageUploadForm_2(request=request,initial={'value': value, 'category': category})
    return render(request, 'new_bill.html', {'form':form})