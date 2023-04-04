import requests
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from .micro_auth_utility import *
from api.serializers import MicrosoftEventSerializer
from api.models import User_info
from .views import firebase_app,auth

class MicrosoftCalendarInitView(APIView):
    
    def get(self, request, *args, **kwargs):
        authorization_header = request.META.get('HTTP_AUTHORIZATION')
        token = authorization_header.replace("Bearer ", "")
        
        decoded_token = auth.verify_id_token(token)
        firebase_user_id = decoded_token['user_id']
        User_info.objects.filter(user_firebase_token=firebase_user_id).update(calender_onboarding_status=True)
        
        flow = get_sign_in_flow()
        try:
            request.session['auth_flow'] = flow
        except Exception as e:
            print(e)
        return HttpResponseRedirect(flow['auth_uri'])

class MicrosoftCallback(APIView):
    
    def get(self, request, *args, **kwargs):
        try:
            result = get_token_from_code(request)
            request.session['micro_credentials'] = result
            access_token = result['access_token']
            #Just checking access token
            graph_url = 'https://graph.microsoft.com/v1.0/me/calendar/events'
            response = requests.get(
                url="{0}/".format(graph_url),
                headers={"Authorization": "Bearer {0}".format(access_token)},
            )
            return redirect('http://localhost:3000/calendar')
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class MicrosoftEvent(APIView):
    
    def get(self, request, *args, **kwargs):
        try :
            authorization_header = request.META.get('HTTP_AUTHORIZATION')
            token = authorization_header.replace("Bearer ", "")
            
            decoded_token = auth.verify_id_token(token)
            firebase_user_id = decoded_token['user_id']
            #firebase_user_id = "DL7rKD68CEYEpNd9eTIjBF6QDbt2"
        
            access_token = (request.session['micro_credentials']).get('access_token')
            graph_url = "https://graph.microsoft.com/v1.0/me/calendar/events"
            response = requests.get(
                url="{0}/".format(graph_url),
                headers={"Authorization": "Bearer {0}".format(access_token)},
            )
            calender_event = response.json()
            #print(calender_event)
            calender_event_value = calender_event.get('value')
            for event in calender_event_value:
                event_dic = {}
                if event.get('isOnlineMeeting'):
                    event_dic['user_firebase_token'] = firebase_user_id
                    event_dic['calender_meeting_id'] = event.get('id')
                    event_dic['lastModifiedDateTime_microsoft'] = event.get('lastModifiedDateTime')
                    event_dic['start_time'] = event.get('start').get('dateTime')
                    event_dic['end_time'] = event.get('end').get('dateTime')
                    if event.get('location').get('displayName') is None :
                        event_dic['location'] = " "
                    else :
                        event_dic['location'] = event.get('location').get('displayName')
                    if event.get('attendees') is None :
                        event_dic['attendees_count'] = 0
                    else :
                        event_dic['attendees_count'] = len(event.get('attendees'))
                    event_dic['meet_link'] = event.get('onlineMeeting').get('joinUrl')
                    event_dic['calendar_platform'] = 'microsoft'

                    if (event_dic['meet_link']).find('google') != -1:
                        event_dic['meet_platform'] = 'google'
                    elif (event_dic['meet_link']).find('zoom') != -1:
                        event_dic['meet_platform'] = 'zoom'
                    elif (event_dic['meet_link']).find('team') != -1:
                        event_dic['meet_platform'] = 'team'
                    microsoft_calender_event_serializer = MicrosoftEventSerializer(data=event_dic)
                    microsoft_calender_event_serializer.is_valid(raise_exception=True)
                    if (microsoft_calender_event_serializer.is_valid()):
                        microsoft_calender_event_serializer.save()
            return redirect('http://localhost:3000/calendar')
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)









