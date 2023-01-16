from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from api.serializers import User_info_Serializers,Summary_Serializers,FileSerializer
from api.models import User_info,Summary
from api.tasks import summarization_function
from .permissions import user_auth_required
from config import base_path_file

import datetime

# View Starts here

class LandingPageAPI(APIView):
    
    permission_classes = user_auth_required()
    
    def get(self, request):
        user = request.user
        email = "test0991@test.com" #request.email
        
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
                
        main_queryset = Summary.objects.filter(user_id=user_id)
        main_queryset_serializer = Summary_Serializers(main_queryset, many=True)
        return Response({"data":{"meetings":main_queryset_serializer.data,
                                 "total_meetings":len(main_queryset_serializer.data),
                                 "recent_meetings":"",
                                 "scheduled_meetings":"",
                                 "summrized_meetings":""}
                         },status=status.HTTP_200_OK)
    
class AddMeetingAPI(APIView):
    
    permission_classes = user_auth_required()
    
    def post(self, request):
        data = JSONParser().parse(request)
        user_id= data['user_id']
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
        #celery task
        #summarization_function(meeting_audio_file_link_new,file=False)
        return Response({"data":
                        {"meeting_id":main_queryset_summary.meeting_id}},
                        status=status.HTTP_201_CREATED)
    
class AddMeetingFileAPI(APIView):
    
    permission_classes = user_auth_required()
    
    def post(self, request, meeting_id):
        file_serializer = FileSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            pathOfFile = file_serializer.data['file']
            newPath = base_path_file + '/' + pathOfFile
            Summary.objects.filter(meeting_id=meeting_id).update(meeting_audio_file_link=newPath)
            #celery task
            #summarization_function(newPath,file=True)
        return Response({"data":{"meeting_id":meeting_id,"status":"File uploaded successfully"}},status=status.HTTP_201_CREATED)
    
class SummaryPagegAPI(APIView):
    
    permission_classes = user_auth_required()
    
    def get(self, request, meeting_id):
        main_queryset = Summary.objects.filter(meeting_id=meeting_id)
        main_queryset_serializer = Summary_Serializers(main_queryset,many=True)
        return Response({"data":{"meeting_data":main_queryset_serializer.data}},status=status.HTTP_200_OK)
    

# wget.download("https://firebasestorage.googleapis.com/v0/b/iitm-f916f.appspot.com/o/male.wav?alt=media&token=f2494f50-284d-42df-a7ff-332dd2a1777a")