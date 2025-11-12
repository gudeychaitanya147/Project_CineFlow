import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def get_authenticated_cred(client_secret_file="./Utilities/Keys/google_client_secret.json", token_file="./Utilities/Keys/google_token.pickle"):
        
    scopes = [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube.force-ssl",
        "https://www.googleapis.com/auth/youtubepartner",
        "https://www.googleapis.com/auth/youtube",
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/spreadsheets"
    ]
    cred = None

    if os.path.exists(token_file):
        with open(token_file, "rb") as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
        cred = flow.run_local_server(port=0)
        cred.refresh(Request())
        with open(token_file, "wb") as token:
            pickle.dump(cred, token)

    return cred

def get_authenticated_apps(app_name, cred):
    versions = {"youtube": "v3", "drive": "v3", "sheets": "v4"}
    for key, version in versions.items():
        if key == app_name:
            service = build(key, version, credentials=cred)
            print(f"\nAuthenticated {key.capitalize()} service...")
            return service
