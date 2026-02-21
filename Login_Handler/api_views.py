import pytz
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json

from Login_Handler.models import List_of_categories, User_Profile
from . import utils


def auth_status(request):
    if request.user.is_authenticated:
        try:
            User_Profile.objects.get(user=request.user)
            needs_setup = False
        except User_Profile.DoesNotExist:
            needs_setup = True
        return JsonResponse({
            'authenticated': True,
            'username': request.user.username,
            'needs_setup': needs_setup,
        })
    return JsonResponse({'authenticated': False, 'username': None, 'needs_setup': False})


@csrf_exempt
@require_http_methods(['POST'])
def auth_logout(request):
    logout(request)
    return JsonResponse({'ok': True})


def timezones(request):
    return JsonResponse({'timezones': pytz.common_timezones})


@login_required
def categories(request):
    if request.method == 'GET':
        categories_obj, _ = List_of_categories.objects.get_or_create(
            user=request.user,
            defaults={'categories': ['Food', 'Games', 'Cinema', 'Petrol']}
        )
        creds, creds_data, service = utils.create_service(request)
        if service is None:
            return JsonResponse({'error': 'Drive service unavailable'}, status=503)
        folder_id = utils.folder_check_create(service)
        utils.folder_check_create(service, folder_id, categories_obj.categories)
        uuid_dict = utils.uuid_to_list(request, categories_obj.categories)
        request.session['uuids'] = uuid_dict
        rev = utils.reverse_dict(uuid_dict)
        request.session['UUIDS'] = rev
        result = [{'id': i, 'name': name, 'uuid': rev[name]} for i, name in enumerate(categories_obj.categories)]
        return JsonResponse({'categories': result})

    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            name = body.get('name', '').strip()
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        if not name:
            return JsonResponse({'error': 'Name is required'}, status=400)
        categories_obj, _ = List_of_categories.objects.get_or_create(user=request.user, defaults={'categories': []})
        if name in categories_obj.categories:
            return JsonResponse({'error': 'Category already exists'}, status=400)
        categories_obj.categories.append(name)
        categories_obj.save()
        creds, creds_data, service = utils.create_service(request)
        if service:
            folder_id = utils.folder_check_create(service)
            utils.folder_check_create(service, folder_id, categories_obj.categories)
        uuid_dict = utils.uuid_to_list(request, categories_obj.categories)
        request.session['uuids'] = uuid_dict
        rev = utils.reverse_dict(uuid_dict)
        request.session['UUIDS'] = rev
        result = [{'id': i, 'name': n, 'uuid': rev[n]} for i, n in enumerate(categories_obj.categories)]
        return JsonResponse({'categories': result}, status=201)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def category_detail(request, category_id):
    categories_obj = List_of_categories.objects.get(user=request.user)
    cat_list = categories_obj.categories

    if category_id >= len(cat_list):
        return JsonResponse({'error': 'Not found'}, status=404)

    if request.method == 'PATCH':
        try:
            body = json.loads(request.body)
            name = body.get('name', '').strip()
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        if not name:
            return JsonResponse({'error': 'Name is required'}, status=400)
        others = cat_list[:category_id] + cat_list[category_id + 1:]
        if name in others:
            return JsonResponse({'error': 'Category already exists'}, status=400)
        creds, creds_data, service = utils.create_service(request)
        if service:
            folder_id = utils.return_folder_id(service)
            folder = utils.return_folder_id(service, folder_id, [cat_list[category_id]])
            utils.rename_folder(service, folder, name)
            old_cat_name = cat_list[category_id]
            for file_id, file_name in utils.get_files_in_folder(service, folder):
                if file_name.startswith(old_cat_name + '_'):
                    new_file_name = name + file_name[len(old_cat_name):]
                    utils.rename_folder(service, file_id, new_file_name)
        cat_list[category_id] = name
        categories_obj.categories = cat_list
        categories_obj.save()
        uuid_dict = utils.uuid_to_list(request, cat_list)
        request.session['uuids'] = uuid_dict
        rev = utils.reverse_dict(uuid_dict)
        request.session['UUIDS'] = rev
        result = [{'id': i, 'name': n, 'uuid': rev[n]} for i, n in enumerate(cat_list)]
        return JsonResponse({'categories': result})

    if request.method == 'DELETE':
        creds, creds_data, service = utils.create_service(request)
        if service:
            try:
                folder_id = utils.return_folder_id(service)
                folder = utils.return_folder_id(service, folder_id, [cat_list[category_id]])
                service.files().delete(fileId=folder).execute()
            except Exception:
                pass
        cat_list.pop(category_id)
        categories_obj.categories = cat_list
        categories_obj.save()
        uuid_dict = utils.uuid_to_list(request, cat_list)
        request.session['uuids'] = uuid_dict
        rev = utils.reverse_dict(uuid_dict)
        request.session['UUIDS'] = rev
        result = [{'id': i, 'name': n, 'uuid': rev[n]} for i, n in enumerate(cat_list)]
        return JsonResponse({'categories': result})

    return JsonResponse({'error': 'Method not allowed'}, status=405)


def choose_name(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    lmail = request.session.get('gmail')
    if not lmail:
        return JsonResponse({'error': 'No pending OAuth session'}, status=403)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    username = body.get('username', '').strip()
    timezone_val = body.get('timezone', '').strip()

    if not username:
        return JsonResponse({'error': 'username is required'}, status=400)
    if not timezone_val or timezone_val not in pytz.common_timezones:
        return JsonResponse({'error': 'Valid timezone is required'}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Username already taken'}, status=400)

    new_user = User.objects.create_user(username=username, email=lmail)
    new_user.set_unusable_password()
    new_user.save()

    User_Profile.objects.create(user=new_user, timezone=timezone_val)

    creds, creds_data = utils.creds_object(request)
    if not creds:
        return JsonResponse({'error': 'Missing credentials'}, status=403)

    login(request, new_user)

    existing = None
    from Login_Handler.models import GoogleCredentials
    existing = GoogleCredentials.objects.filter(user=new_user).first()
    refresh_token = creds.refresh_token or (existing.refresh_token if existing else None)
    utils.update_db_on_credentials(request, creds, refresh_token)

    List_of_categories.objects.update_or_create(
        user=new_user,
        defaults={'categories': ['Food', 'Games', 'Cinema', 'Petrol']}
    )

    return JsonResponse({'ok': True, 'username': username})
