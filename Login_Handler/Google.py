from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def Create_Service(credentials_dict, api_name='drive', api_version='v3'):
    creds = Credentials(**credentials_dict)
    return build(api_name, api_version, credentials=creds)
