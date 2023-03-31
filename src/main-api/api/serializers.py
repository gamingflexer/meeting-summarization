from rest_framework import serializers
from api.models import *

class Summary_Serializers(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = "__all__"
        
class User_info_Serializers(serializers.ModelSerializer):
    class Meta:
        model = User_info
        fields = "__all__"
        
class FileSerializer(serializers.ModelSerializer):
    class Meta():
        model = File
        fields = ('file', 'timestamp')

class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = ('meeting_id','calender_meeting_id','user_firebase_token','title','creator','organizer','creation_time','start_time','end_time','attendees_count','meet_link','meet_platform','start_time','end_time')