import os

import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_client():
    sa_json = os.environ.get("GOOGLE_SA_JSON", "")
    if not sa_json:
        raise RuntimeError("GOOGLE_SA_JSON not set")
    creds = Credentials.from_service_account_file(sa_json, scopes=SCOPES)
    return gspread.authorize(creds)


def export_rows(spreadsheet_id: str, worksheet: str, rows: list):
    gc = get_client()
    sh = gc.open_by_key(spreadsheet_id)
    ws = sh.worksheet(worksheet)
    ws.append_rows(rows)
