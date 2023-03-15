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
from api.serializers import CalendarEventSerializer
from api.models import Summary
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
import datetime
from django.shortcuts import redirect
from msal import PublicClientApplication
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
                                              maxResults=15, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])

        return JsonResponse({'status': 'success',
                             'message': 'Events have been fetched.',
                             'data': events
                             })


class GoogleCalendarMultipleEventsView(View):
    """
    Fetch events from Google Calendar.
    """

    def get(self, request,api_keyword, *args, **kwargs):

        if (api_keyword == 'all' or api_keyword == 'sync' or api_keyword == 'past' or api_keyword=='upcoming'):
            credentials = Credentials(
                **request.session['credentials']
            )

            service = build('calendar', 'v3', credentials=credentials)

            # Min time
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

            #just to fetch 5 event
            event_count=5
            #fetch upcoming new events
            if api_keyword == 'sync':
                event_count = 20
            events_result = service.events().list(calendarId='primary',timeMin=now,
                                                  maxResults=event_count, singleEvents=True, orderBy='startTime').execute()
            events = events_result.get('items', [])
            eventslist =[]

            for event in events :
                eventdict = {}
                eventdict['user_id'] = 1
                eventdict['calender_meeting_id'] = event.get('id')
                eventdict['title'] = event.get('summary')
                eventdict['creator'] = (event.get('creator')).get('email')
                eventdict['organizer'] = (event.get('organizer')).get('email')
                eventdict['creation_time'] = event.get('created')
                eventdict['start_time'] = (event.get('start')).get('dateTime')
                eventdict['end_time'] = (event.get('end')).get('dateTime')
                if event.get('attendees') is None :
                    eventdict['attendees_count'] = 0
                else :
                    eventdict['attendees_count'] = len(event.get('attendees'))
                eventdict['meet_link'] = event.get('location')
                eventdict['meet_platform'] = 'unknown'
                if eventdict['meet_link'] is None :
                    eventdict['meet_link'] = event.get('hangoutLink')
                if eventdict['meet_link'] is not None :
                    if eventdict['meet_link'] == "" or eventdict['meet_link'].find('https://') == -1 :
                        eventdict['meet_link'] = event.get('hangoutLink')

                if eventdict['meet_link'] is None:
                    eventdict['meet_link'] = ''
                if (eventdict['meet_link']).find('google') !=-1 :
                    eventdict['meet_platform'] = 'Google Meet'
                elif (eventdict['meet_link']).find('zoom') !=-1  :
                    eventdict['meet_platform'] = 'Zoom'
                elif (eventdict['meet_link']).find('team') !=-1  :
                    eventdict['meet_platform'] = 'Teams'

                calender_event_serializer=CalendarEventSerializer(data=eventdict)
                # calender_event_serializer.is_valid(raise_exception=True)
            if (calender_event_serializer.is_valid()):
                calender_event_serializer.save()
            if api_keyword == 'all':
                event_data = Summary.objects.filter(user_id=1)
                calender_event_serializer_data = CalendarEventSerializer(event_data, many=True)
            elif api_keyword == 'sync' or api_keyword == 'upcoming':
                event_data = Summary.objects.filter(
                    start_time__gte=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"), user_id=1)
                calender_event_serializer_data = CalendarEventSerializer(event_data, many=True)
            elif api_keyword == 'past':
                event_data = Summary.objects.filter(
                    start_time__lt=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"), user_id=1)
                calender_event_serializer_data = CalendarEventSerializer(event_data, many=True)
            return JsonResponse({
                                 'data': calender_event_serializer_data.data
                                 })
        else :
            Response(status=status.HTTP_404_NOT_FOUND)




