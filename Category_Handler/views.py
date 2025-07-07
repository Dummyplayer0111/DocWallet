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
            name = form.cleaned_data['name']
            id = utils.create_date_folder(request,UUID)
            print(id)
            print(dict(request.session))
            new_uuid = utils.upload_image_and_session_update(request,id,image,UUID)
            print(dict(request.session))
            return render(request, 'bills_page.html', {'uuid':new_uuid})
    else:
        print(dict(request.session))
        utils.create_date_folder(request,UUID)
        print(dict(request.session))
        form = ImageUploadForm()
    return render(request, 'new_bill.html', {'form':form})