from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.views import View
from django.http import JsonResponse
from django.shortcuts import redirect

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'


class GoogleCalendarInitView(View):

    def get(self, request, *args, **kwargs):

        flow = InstalledAppFlow.from_client_secrets_file(
            '../main-api/config/client_secret.json',
            scopes = ['https://www.googleapis.com/auth/calendar.readonly']
        )


        flow.redirect_uri = 'http://localhost:8000/api/rest/v1/calendar/redirect'

        authorization_url, state = flow.authorization_url(

            access_type='offline',

            include_granted_scopes='true',
        )


        request.session['state'] = state

        # Redirect the user to the authorization URL.
        return redirect(authorization_url)


class GoogleCalendarRedirectView(View):
    """
    Callback view to handle the response from Google OAuth2 authorization server.
    This view is registered as the redirect_uri in the Google OAuth2 client
    configuration. The authorization server will redirect the user to this view
    after the user has granted or denied permission to the client.
    """

    def get(self, request, *args, **kwargs):

        state = request.GET.get('state')

        flow = InstalledAppFlow.from_client_secrets_file(
            '../main-api/config/client_secret.json',
            scopes=['https://www.googleapis.com/auth/calendar.readonly','"https://www.googleapis.com/auth/userinfo.email','https://www.googleapis.com/auth/userinfo.profile'],
            state=state
        )
        flow.redirect_uri = 'http://localhost:8000/api/rest/v1/calendar/redirect'

        # Use the authorization server's response to fetch the OAuth 2.0 tokens.
        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)

        # Store the credentials in the session.
        credentials = flow.credentials

        request.session['credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }


        return redirect('http://localhost:8000/api/rest/v1/calendar/events')


class GoogleCalendarEventsView(View):
    """
    Fetch events from Google Calendar.
    """

    def get(self, request, *args, **kwargs):
        credentials = Credentials(
            **request.session['credentials']
        )

        service = build('calendar', 'v3', credentials=credentials)

        # Min time
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

        # Call the Calendar API
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])

        return JsonResponse({'status': 'success',
                             'message': 'Events have been fetched.',
                             'data': events
                             })






