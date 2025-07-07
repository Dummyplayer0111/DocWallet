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
from .forms import ImageUploadForm
from googleapiclient.http import MediaIoBaseUpload

def inside_category(request,UUID):
    return render(request, 'bills_page.html', {'uuid':UUID})

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
            return render(request, 'bills_page.html',{'uuid':UUID})
    else:
        form = ImageUploadForm()
    return render(request, 'new_bill.html', {'form':form})