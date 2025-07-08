import os,pytz,uuid
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests
from .forms import CustomUserCreationForm,CategoryForm
from .Google import Create_Service
from django.contrib.auth.decorators import login_required
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from Login_Handler.models import GoogleCredentials,List_of_categories,User_Profile
from django.utils.timezone import make_aware, is_naive
from django.utils import timezone
from datetime import datetime
from google.auth.transport.requests import Request
from . import utils

@csrf_exempt
def auth_receiver(request):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    state = request.session.get('state')
    if not state:
        return HttpResponse("Missing OAuth state", status=400)
    flow = utils.create_flow_object(state)
    flow.redirect_uri = "http://localhost:8000/auth-receiver/"
    authorization_response = request.build_absolute_uri()
    try:
        flow.fetch_token(authorization_response=authorization_response)
    except Exception as e:
        return HttpResponse(f"Failed to fetch token: {e}", status=400)
    credentials = utils.session_update(request,flow.credentials)
    idinfo = id_token.verify_oauth2_token(
        credentials.id_token, requests.Request(), os.environ['GOOGLE_OAUTH_CLIENT_ID']
    )
    print("NOW:", datetime.utcnow())
    print("EXPIRY:", credentials.expiry)
    print("EXPIRED?", credentials.expired)
    email = idinfo['email']
    request.session['gmail'] = email
    user = User.objects.filter(email=email).first()
    if user:
        login(request, user)
        existing = GoogleCredentials.objects.filter(user=user).first()
        refresh_token = credentials.refresh_token or (existing.refresh_token if existing else None)
        utils.update_db_on_credentials(request,credentials,refresh_token)
        return redirect('home')
    else:
        return redirect('choose_name')   

def sign_in(request):
    return render(request, 'sign_in.html')

def oauth2_start(request):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    flow=utils.create_flow_object()
    flow.redirect_uri = "http://localhost:8000/auth-receiver/"

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='select_account'
    )
    request.session['state'] = state  
    return redirect(authorization_url)
    
def choose_name(request):
    lmail = request.session.get('gmail')
    if not lmail:
        return redirect('sign_in')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            new_user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=lmail
            )
            new_user.set_unusable_password()
            new_user.save()

            User_Profile.objects.create(user = new_user,timezone=form.cleaned_data['timezone'])

            creds, creds_data = utils.creds_object(request)
            if not creds:
                return HttpResponse("Missing or invalid credentials", status=403)

            login(request, new_user)

            existing = GoogleCredentials.objects.filter(user=new_user).first()
            refresh_token = creds.refresh_token or (existing.refresh_token if existing else None)
            utils.update_db_on_credentials(request,creds,refresh_token)
            List_of_categories.objects.update_or_create(user=request.user, defaults={'categories': ['Food', 'Games', 'Cinema', 'Petrol']})
            return redirect('home')
    else:
        username_guess = lmail.split('@')[0]
        form = CustomUserCreationForm(initial={'username': username_guess})
    return render(request, 'choose_name.html', {'form': form})

@login_required
def home(request):
    creds, creds_data, service = utils.create_service(request)
    if creds is None:
        return HttpResponse("Something is wrong please login again", status=403)
    folder_id = utils.folder_check_create(service)
    categories_obj, created = List_of_categories.objects.get_or_create(user=request.user,defaults={'categories': ['Food', 'Games', 'Cinema', 'Petrol']})
    folders = utils.folder_check_create(service,folder_id,categories_obj.categories)
    UUID_DICT = utils.uuid_to_list(request,categories_obj.categories)
    request.session['uuids'] = UUID_DICT
    UUID_DICT = utils.reverse_dict(UUID_DICT)
    request.session['UUIDS'] = UUID_DICT
    return render(request, 'home.html', {'UUID_DICT':UUID_DICT})

def edit(request,category_id=None):
    categories_obj = List_of_categories.objects.get(user=request.user)
    if category_id is not None:
        try:
            creds, creds_data, service = utils.create_service(request)
            l = categories_obj.categories
            folder_id = utils.return_folder_id(service)
            folder = utils.return_folder_id(service,folder_id,[l[int(category_id)]])
            service.files().delete(fileId=folder).execute()
            l.pop(int(category_id))
            categories_obj.categories = l
            categories_obj.save()
            folders = utils.folder_check_create(service,folder_id,categories_obj.categories)
            return render(request, 'edit.html', {'categories':{i: value for i, value in enumerate(categories_obj.categories)}})
        except:
            return render(request, 'edit.html', {'categories':{i: value for i, value in enumerate(categories_obj.categories)}})
    else:
        return render(request, 'edit.html', {'categories':{i: value for i, value in enumerate(categories_obj.categories)}})

def add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            name=form.cleaned_data['name'].strip()
            categories_obj = List_of_categories.objects.get(user=request.user)
            l = categories_obj.categories
            if name not in categories_obj.categories:
                l.append(name)
                categories_obj.categories=l
                categories_obj.save()
                creds, creds_data, service = utils.create_service(request)
                folder_id = utils.return_folder_id(service)
                folders = utils.folder_check_create(service,folder_id,categories_obj.categories)
            else:
                form.add_error('name', 'This category name already exists')
                return render(request, 'add.html', {'form': form})
            return redirect('edit')  
    else:
        form = CategoryForm()
    return render(request, 'add.html', {'form': form})

def rename(request,category_id):
    creds, creds_data, service = utils.create_service(request)
    folder_id = utils.return_folder_id(service)
    categories_obj = List_of_categories.objects.get(user=request.user)
    l = categories_obj.categories
    c_name = l[int(category_id)]
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            name=form.cleaned_data['name'].strip()
            if name in (l[:int(category_id)] + l[int(category_id+1):]):
                form.add_error('name', 'This category name already exists.')
                return render(request, 'rename.html', {'form': form})
            else:
                folder = utils.return_folder_id(service,folder_id,[l[int(category_id)]])
                l[int(category_id)] = name
                categories_obj.categories = l
                categories_obj.save()
                utils.rename_folder(service,folder,name)
        return redirect('edit')
    else:
        form = CategoryForm(initial={'name':c_name})
    return render(request, 'rename.html', {'form': form})