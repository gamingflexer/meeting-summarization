from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import datetime
from api.models import User_info,Summary
from api.serializers import User_info_Serializers,Summary_Serializers
from .permissions import user_auth_required

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
    
    def get(self, request):
        user = request.user
        data = request.data
        main_queryset_serializer_summary = Summary_Serializers(data = data)
        if main_queryset_serializer_summary.is_valid():
            main_queryset_serializer_summary.save()
        return Response({"data":""},status=status.HTTP_201_CREATED)