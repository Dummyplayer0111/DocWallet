import os,pytz,uuid,io,datetime
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests
from .forms import CustomUserCreationForm,CategoryForm,ImageUploadForm
from .Google import Create_Service
from django.contrib.auth.decorators import login_required
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from Login_Handler.models import GoogleCredentials,List_of_categories,User_Profile
from django.utils import timezone
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseUpload
from django.utils.timezone import make_aware, is_naive
from decimal import Decimal

def creds_object(request,hit_db = False):
    if hit_db:
        record = GoogleCredentials.objects.filter(user=request.user).first()
        if not record:
            return None,None
        creds_data_f = {
            'token': record.token,
            'refresh_token': record.refresh_token,
            'token_uri': record.token_uri,
            'client_id': os.environ['GOOGLE_OAUTH_CLIENT_ID'],
            'client_secret': os.environ['GOOGLE_OAUTH_CLIENT_SECRET'],
            'scopes': record.scopes.split() if isinstance(record.scopes, str) else record.scopes,
        }

        creds_f = Credentials(
            token=creds_data_f['token'],
            refresh_token=creds_data_f.get('refresh_token'),
            token_uri=creds_data_f['token_uri'],
            client_id=creds_data_f['client_id'],
            client_secret=creds_data_f['client_secret'],
            scopes=creds_data_f['scopes'] if isinstance(creds_data_f['scopes'], list) else creds_data_f['scopes'].split()
        )
        return creds_f,creds_data_f

    else:
        creds_data_f = request.session.get('credentials')
        if not creds_data_f:
             return None,None
        creds_f = Credentials(
        token=creds_data_f['token'],
        refresh_token=creds_data_f.get('refresh_token'),
        token_uri=creds_data_f['token_uri'],
        client_id=creds_data_f['client_id'],
        client_secret=creds_data_f['client_secret'],
        scopes=creds_data_f['scopes'].split() if isinstance(creds_data_f['scopes'], str) else creds_data_f['scopes']
        )
        return creds_f,creds_data_f
        
def update_db_on_credentials(request, creds_f,refresh_token=None):

    if refresh_token:
        GoogleCredentials.objects.update_or_create(
        user=request.user,
        defaults={
            'token': creds_f.token,
            'refresh_token': refresh_token,
            'token_uri': creds_f.token_uri,
            'scopes': ' '.join(creds_f.scopes),
            'expiry': make_aware(creds_f.expiry) if creds_f.expiry and timezone.is_naive(creds_f.expiry) else creds_f.expiry,
            }
        )


    else:
        GoogleCredentials.objects.update_or_create(
        user=request.user,
        defaults={
            'token': creds_f.token,
            'refresh_token': creds_f.refresh_token,
            'token_uri': creds_f.token_uri,
            'scopes': ' '.join(creds_f.scopes),
            'expiry': make_aware(creds_f.expiry) if creds_f.expiry and timezone.is_naive(creds_f.expiry) else creds_f.expiry,
            }
        )

def create_flow_object(state_f=None):
    if state_f:
        flow_f = Flow.from_client_config(
        {
            "web": {
                "client_id": os.environ['GOOGLE_OAUTH_CLIENT_ID'],
                "client_secret": os.environ['GOOGLE_OAUTH_CLIENT_SECRET'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost:8000/auth-receiver/"],
            }
        },
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/drive",
        ],
        state=state_f 
        )
        return flow_f
    


    else:
        flow_f = Flow.from_client_config(
        {
            "web": {
                "client_id": os.environ['GOOGLE_OAUTH_CLIENT_ID'],
                "client_secret": os.environ['GOOGLE_OAUTH_CLIENT_SECRET'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost:8000/auth-receiver/"],
            }
        },
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/drive",
        ],
        )
        return flow_f
    
def session_update(request,credentials):
        
    request.session['credentials'] = {
    'token': credentials.token,
    'refresh_token': getattr(credentials, 'refresh_token', None),
    'token_uri': credentials.token_uri,
    'client_id': credentials.client_id,
    'client_secret': credentials.client_secret,
    'scopes': credentials.scopes,
    'expiry': credentials.expiry.isoformat() if credentials.expiry else None,
    }
    return credentials

def folder_check_create(service,parent_id=None,target_names=['DocWallet']):
    query = None
    if parent_id:
        query = (
            f"'{parent_id}' in parents and "
            "mimeType='application/vnd.google-apps.folder' and trashed=false and "
            "(" + " or ".join([f"name='{name}'" for name in target_names]) + ")"
        )
    else:
         query=f"name='{target_names[0]}' and mimeType='application/vnd.google-apps.folder' and trashed=false"

    response = service.files().list(q=query,spaces='drive',fields='files(id, name)').execute()
    existing_folders = {f['name']: f['id'] for f in response.get('files', [])}
    created_ids = {}
    for name in target_names:
        if name not in existing_folders:
            metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_id:
                metadata['parents'] = [parent_id]
            created = service.files().create(body=metadata, fields='id').execute()
            created_ids[name] = created['id']
            print(f"Created folder '{name}' with ID: {created['id']}")
        else:
            created_ids[name] = existing_folders[name]
            print(f"Folder '{name}' already exists with ID: {existing_folders[name]}")
    if not parent_id and len(target_names) == 1:
        return created_ids[target_names[0]]
    return created_ids

def create_service(request):
    creds, creds_data = creds_object(request,True)
    if not creds:
        return None,None,None
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    elif creds.expired and not creds.refresh_token:
        return None,None,None
    update_db_on_credentials(request,creds)
    service = build('drive', 'v3', credentials=creds)
    return creds,creds_data,service

def return_folder_id(service, parent_id=None, target_names=['DocWallet']):
    if parent_id:
        query = (
            f"'{parent_id}' in parents and "
            "mimeType='application/vnd.google-apps.folder' and trashed=false and "
            "(" + " or ".join([f"name='{name}'" for name in target_names]) + ")"
        )
    else:
         query=f"name='{target_names[0]}' and mimeType='application/vnd.google-apps.folder' and trashed=false"

    response = service.files().list(q=query,spaces='drive',fields='files(id, name)').execute()
    files = response.get('files',[])
    return files[0]['id']

def rename_folder(service, folder_id, new_name):
    file_metadata = {'name': new_name}
    updated_folder = service.files().update(
        fileId=folder_id,
        body=file_metadata,
        fields='id, name'
    ).execute()
    print(f"Renamed folder to: {updated_folder['name']} (ID: {updated_folder['id']})")
    return updated_folder['id']

def uuid_to_list(request,items):
    #uuid_dict = {str(uuid.uuid4()): item for item in items}
    uuid_dict={}
    for item in items:
        key = str(uuid.uuid4())
        while key in uuid_dict:
            key = str(uuid.uuid4())
        uuid_dict[key] = item
    request.session['UUIDS'] = uuid_dict
    return uuid_dict

def reverse_dict(d):
    return {v: k for k, v in d.items()}

def upload_image_to_drive(service,file_obj,filename,mimetype='image/jpeg',folder_id=None):
    file_metadata = {'name':filename}
    if folder_id:
        file_metadata['parents'] = [folder_id]
    media = MediaIoBaseUpload(file_obj, mimetype=mimetype)

    uploaded = service.files().create(body=file_metadata,media_body=media,fields='id, name').execute()
    service.permissions().create(fileId=uploaded['id'],body={"role": "reader", "type": "anyone"},).execute()
    return uploaded

def image_name(request,UUID,value):
    names = request.session.get('uuids')
    cat_name = names.get(UUID)
    user_profile = User_Profile.objects.get(user=request.user)
    user_tz = pytz.timezone(user_profile.timezone)
    timezone.activate(user_tz)
    now = timezone.localtime()
    time_name = str(now)[:19]
    time_name = time_name.replace(" ",'_')
    value_name = "{:012.2f}".format(value)
    return cat_name + "_" + time_name + "_" + value_name

def return_cat_name(request,UUID):
    names = request.session.get('uuids')
    cat_name = names.get(UUID)
    return cat_name

def get_image_file_names_in_folder(service, folder_id):
    query = (
        f"'{folder_id}' in parents and "
        "mimeType contains 'image/' and trashed = false"
    )
    image_names = []
    page_token = None

    while True:
        response = service.files().list(
            q=query,
            spaces='drive',
            fields='nextPageToken, files(name, mimeType)',
            pageToken=page_token
        ).execute()

        for file in response.get('files', []):
            image_names.append(file['name'])

        page_token = response.get('nextPageToken')
        if not page_token:
            break

    return image_names

def randomizer(request):
    categories_obj = List_of_categories.objects.get(user = request.user)
    UUID_DICT = uuid_to_list(request,categories_obj.categories)
    request.session['uuids'] = UUID_DICT
    UUID_DICT = reverse_dict(UUID_DICT)
    request.session['UUIDS'] = UUID_DICT

def list_of_bills(request,UUIDS,start_date=None,end_date=None):
    creds,creds_data,service = create_service(request)
    folder_id = return_folder_id(service)
    l,l1=[],[]
    for UUID in UUIDS:
        cat_id = return_folder_id(service,folder_id,[return_cat_name(request,UUID)])
        l = l + get_image_file_names_in_folder(service,cat_id)

    if start_date is None:
        return l

    elif start_date:
        user_profile = User_Profile.objects.get(user=request.user)
        user_tz = pytz.timezone(user_profile.timezone)
        timezone.activate(user_tz)
        for x in l:
            props = x.split('_')
            date_str = props[1]
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            if date_obj >= start_date and date_obj <= end_date:
                l1.append(x)
        return l1

def names_to_uuid(request,categories):
    l=[]
    names = request.session.get('UUIDS')
    for i in categories:
        l.append(names.get(i))
    return l

def table_data(request):
    l = request.session.get('Final_bills')
    l1 = []
    s = Decimal('0')
    for x in l:
        l2 = x.split('_')
        l2[3] = str(float(l2[3]))
        temp = Decimal(l2[3])
        s = s+temp
        l3=[]
        l3.append(l2[1])
        l3.append(l2[2])
        l3.append(l2[0])
        l3.append(l2[3])
        l1.append(l3)
    l1.append(["","","TOTAL:",f"{s:.2f}"])
    return l1

def get_image_link(service, file_name):
    # Search for image file by name
    query = f"name = '{file_name}' and mimeType contains 'image/' and trashed = false"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields="files(id, name, mimeType)",
        pageSize=1
    ).execute()

    items = results.get('files', [])
    if not items:
        return None

    file_id = items[0]['id']
    
    # Construct the sharable link (assumes file is shared)
    image_link = f"https://drive.google.com/uc?id={file_id}"
    return image_link

def get_image_id(service,name):
    query = (
        f"name = '{name}' and "
        "mimeType contains 'image/' and "
        "trashed = false"
    )
    response = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, mimeType)',
        pageSize=1
    ).execute()

    files = response.get('files', [])
    if not files:
        return None

    return files[0]['id']

def delete_file(service, file_id):
    try:
        service.files().delete(fileId=file_id).execute()
        print(f"Deleted file with ID: {file_id}")
        return True
    except Exception as e:
        print(f"Failed to delete file: {file_id} — {e}")
        return False
