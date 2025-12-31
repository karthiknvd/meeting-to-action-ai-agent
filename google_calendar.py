from __future__ import print_function
import datetime
import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Scopes define what permissions your app has
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Authenticate and return Google Calendar service."""
    creds = None

    # Token file stores the user's access and refresh tokens
    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as token:
            creds = pickle.load(token)

    # If no valid credentials are available, prompt login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pkl", "wb") as token:
            pickle.dump(creds, token)

    service = build("calendar", "v3", credentials=creds)
    return service


def add_event_to_calendar(summary, description, start_time):
    """Add a single event to Google Calendar."""
    service = get_calendar_service()

    # Ensure start_time is datetime
    if isinstance(start_time, str):
        start_time = datetime.datetime.fromisoformat(start_time)

    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': (start_time + datetime.timedelta(hours=1)).isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
    }

    event_result = service.events().insert(calendarId='primary', body=event).execute()
    print(f"✅ Event created: {event_result.get('htmlLink')}")
    return event_result.get('htmlLink')
