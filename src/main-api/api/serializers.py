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
        fields = ('meeting_id','calender_meeting_id','user_firebase_token','title','creator','organizer','creation_time','start_time','end_time','attendees_count','meet_link','meet_platform')
        
class MicrosoftEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = ('calender_meeting_id','lastModifiedDateTime_microsoft','start_time','end_time','meeting_location','attendees_count','meet_link','calendar_platform','meet_platform')

