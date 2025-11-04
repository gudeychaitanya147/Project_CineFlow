import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Full access to read/write Sheets

def get_authenticated_service(client_secret_file="client_secret.json", token_file="token_drive.pickle"):
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    """Authenticate with Google Sheets API and return a service instance."""
    creds = None

    # Reuse existing credentials if available
    if os.path.exists(token_file):
        with open(token_file, "rb") as token:
            creds = pickle.load(token)

    # Refresh or log in if credentials invalid
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
            creds = flow.run_local_server(port=0)
        with open(token_file, "wb") as token:
            pickle.dump(creds, token)

    # Build Sheets API client
    service = build("sheets", "v4", credentials=creds)
    return service

def list_sheets(service, spreadsheet_id):
    """List all sheet names in the spreadsheet."""
    metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = metadata.get("sheets", [])
    names = [s["properties"]["title"] for s in sheets]
    print("Available Sheets:", names)
    return names

def read_sheet(service, spreadsheet_id, range_name):
    """Read data from a given Google Sheet range."""
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()
    values = result.get("values", [])
    return values


def write_sheet(service, spreadsheet_id, range_name, values):
    """Write data (2D list) to a given range in Google Sheet."""
    body = {"values": values}
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="RAW",
        body=body
    ).execute()
    print(f"{result.get('updatedCells')} cells updated.")


SHEET_ID = "1ttrGdA9cTP5Qei8P2zp_d0klbUPLkIGiUbTfvsAWhSg"
