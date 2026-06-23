import datetime
import pickle
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

class CalendarFetcher:
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    def __init__(self, creds_file='credentials.json', token_file='token.pickle'):
        self.creds_file = creds_file
        self.token_file = token_file
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.creds_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        return build('calendar', 'v3', credentials=creds)

    def get_upcoming_events(self, days=7) -> list:
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        end = (datetime.datetime.utcnow() + datetime.timedelta(days=days)).isoformat() + 'Z'
        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=end,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        formatted = []
        for e in events:
            start = e['start'].get('dateTime', e['start'].get('date'))
            formatted.append({
                'summary': e.get('summary', 'Sin título'),
                'start': start,
                'link': e.get('htmlLink', '')
            })
        return formatted