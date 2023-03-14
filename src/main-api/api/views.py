from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from drf_yasg import openapi

from api.serializers import User_info_Serializers,Summary_Serializers,FileSerializer
from api.models import User_info,Summary
from api.tasks import summarization_function
from .permissions import user_auth_required
from config import base_path_file
from authentication.models import User
from decouple import config
from utils import txt_to_pdf
import datetime
import os

from django.core.exceptions import ObjectDoesNotExist

DEBUG = config('DEBUG', cast=bool)

# View Starts here

# ONBOARDING API

class OnboardingAPI(APIView): # ???
    
    permission_classes = user_auth_required()
    
    def post(self, request):        
        data = (JSONParser().parse(request))['data']
        user_id = data['user_id']
        main_queryset = User_info.objects.get(user_id=user_id)
        data_inserted = {"user_prof_type":data['user_prof_type'],
                         "user_meeting_category":data['user_meeting_category'],
                         "email" : data['email']}
        main_queryset_serializer = User_info_Serializers(main_queryset,data=data_inserted)
        if main_queryset_serializer.is_valid():
            main_queryset_serializer.save()
            return Response({"data":main_queryset_serializer.data},status=status.HTTP_200_OK)
        return Response(main_queryset_serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class LandingPageAPI(APIView):
    
    permission_classes = user_auth_required()
    
    def get(self, request):
        user = request.user
        email = "test0991@test.com" #request.email
        user_id = 1
        main_queryset = User_info.objects.filter(email=email)
        if main_queryset.exists():
            main_queryset = main_queryset.first()
            main_queryset_serializer = User_info_Serializers(main_queryset)
            user_id = main_queryset.user_id
        else:
            main_queryset = User_info.objects.create(email=email)
            main_queryset_serializer = User_info_Serializers(data = main_queryset)
            if main_queryset_serializer.is_valid():
                main_queryset_serializer.save()
                
        main_queryset_total_meetings = Summary.objects.filter(user_id=user_id)
        main_queryset_summarized = Summary.objects.filter(user_id=user_id)
        main_queryset = Summary.objects.filter(user_id=user_id).order_by('-meeting_id')[:4][::-1]
        main_queryset_serializer = Summary_Serializers(reversed(main_queryset), many=True)
        return Response({"data":{"meetings":(main_queryset_serializer.data),
                                 "total_meetings":len(main_queryset_total_meetings),
                                 "recent_meetings":"",
                                 "scheduled_meetings":"",
                                 "summrized_meetings":len(main_queryset_summarized)}
                         },status=status.HTTP_200_OK)
    
class AddMeetingAPI(APIView):
    
    permission_classes = user_auth_required()
    
    @csrf_exempt
    def post(self, request):
        data = JSONParser().parse(request)
        user_id = data['user_id']
        meeting_audio_file_link_new = ""
        if data.get("is_summarized"):
            meeting_audio_file_link_new = data.get("meeting_audio_file_link")
        main_queryset = User_info.objects.get(user_id=user_id)
        Summary.objects.create(user_id = main_queryset,
                                scheduled_meeting = data.get("scheduled_meeting"), 
                                meeting_description = data.get("meeting_description"),
                                scheduled_meeting_time = datetime.datetime.strptime(data.get("scheduled_meeting_time"), '%Y-%m-%d %H:%M:%S'),
                                meeting_location = data.get("meeting_location"),
                                meeting_transcript = data.get("meeting_transcript"),
                                is_multilingual = data.get("is_multilingual"),
                                language = data.get("language"),
                                is_summarized = False,
                                meeting_audio_file_link = meeting_audio_file_link_new,
                                )
        main_queryset_summary = Summary.objects.filter(user_id=user_id).latest('meeting_id')
        main_queryset_summary_serializer = Summary_Serializers(main_queryset_summary)
        #celery task
        #summarization_function(meeting_audio_file_link_new,file=False)
        return Response({"data":
                        {"meeting_data":main_queryset_summary_serializer.data}},
                        status=status.HTTP_201_CREATED)
    
class AddMeetingFileAPI(APIView):
    
    permission_classes = user_auth_required()
    #Swagger Part
    token_param_config = openapi.Parameter('meeting_id', in_= openapi.IN_QUERY, description='meeting_id', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    @csrf_exempt
    def post(self, request, meeting_id):
        file_serializer = FileSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            pathOfFile = file_serializer.data['file']
            newPath = base_path_file + '/' + pathOfFile
            Summary.objects.filter(meeting_id=meeting_id).update(meeting_audio_file_link=newPath,is_summarized=True)
            #make it celery task
            summary,transcript = summarization_function(newPath,file=True)
            Summary.objects.filter(meeting_id=meeting_id).update(meeting_summary=summary,meeting_transcript=transcript)
        return Response({"data":{"meeting_id":meeting_id,"status":"File uploaded successfully"}},status=status.HTTP_201_CREATED)
    
class SummaryPageAPI(APIView):
    
    permission_classes = user_auth_required()
    
    def get(self, request, meeting_id):
        email = "surve790@gmail.com" #request.email
        try:
            main_queryset = Summary.objects.get(meeting_id=meeting_id)
        except ObjectDoesNotExist:
            return Response({"data":{"error":"Meeting Summary does not exist"}},status=status.HTTP_400_BAD_REQUEST)
        main_queryset_serializer = Summary_Serializers(main_queryset)
        content = main_queryset_serializer.data
        content['top_keywords'] = content['top_keywords'].split(',')
        content['top_speaker'] = content['top_speaker'].split(',')
        content['highlights'] = content['highlights'].split(',')
        content['reading_time'] = str((len(content['meeting_summary'].split(' '))//3 )//60) + ' mins'
        path = os.path.join(base_path_file,"media",f'{meeting_id}.pdf')
        txt_to_pdf(content['meeting_summary'],path)
        return Response({"data":{
            "meeting_data":content,
            "email_redirect":f"mailto:{email}",
            }},status=status.HTTP_200_OK)
    
    
class DownloadpdfAPI(APIView):
    
    permission_classes = user_auth_required()
    
    def get(self,request,meeting_id):
        main_queryset = Summary.objects.filter(meeting_id=meeting_id)
        main_queryset_serializer = Summary_Serializers(main_queryset,many=True)
        content = main_queryset_serializer.data
        path = os.path.join(base_path_file,"media",f'{meeting_id}.pdf')
        txt_to_pdf(content[0]['meeting_summary'],path)
        return Response({"data":{"path" : path}},status=status.HTTP_200_OK)
        

class EditUserDataAPI(APIView) :
    
    permission_classes = user_auth_required()
    
    def get(self,request,username):
        User_data = User.objects.get(username=username)
        User_data_serializer = User_info_Serializers(User_data)
        return Response({"data": {"user_data": User_data_serializer.data}}, status=status.HTTP_200_OK)

    @csrf_exempt
    def post(self,request):
        try :
            data = JSONParser().parse(request)
            user_name = data['username']
            query_set = User.objects.get(username=user_name)
            query_set.save()
            return Response(status=status.HTTP_200_OK)
        except Exception as e :
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
# FEEEDBACK API

class FeedBackAPI(APIView) :
    
    permission_classes = user_auth_required()
    
    def get(self,request,meeting_id,param,val):
        if param == "is_good":
            main_queryset = Summary.objects.filter(meeting_id=meeting_id).update(is_good = val)
        if param == "factual_consistency":
            main_queryset = Summary.objects.filter(meeting_id=meeting_id).update(factual_consistency = val)
            
        return Response(status=status.HTTP_200_OK)
    
# ANALYTICS API

class AnalyticsAPI(APIView) : # ??
    
    permission_classes = user_auth_required()
    
    def get(self,request,user_id):
        main_queryset = Summary.objects.filter(meeting_id=user_id)
        main_queryset_serializer = Summary_Serializers(main_queryset,many=True)
        content = main_queryset_serializer.data
        return Response({"data": {"analytics_data": content}}, status=status.HTTP_200_OK)
    
    
# EDIT SUMMARY API

class EditSummaryAPI(APIView) : # ??
    
    permission_classes = user_auth_required()
    
    @csrf_exempt
    def post(self,request):
        try :
            data = JSONParser().parse(request)
            meeting_id = data['meeting_id']
            query_set = Summary.objects.get(meeting_id=meeting_id)
            query_set.save()
            return Response(status=status.HTTP_200_OK)
        except Exception as e :
            return Response(status=status.HTTP_400_BAD_REQUEST)