from rest_framework import serializers
from api.models import *

class Summary_Serializers(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = ('meeting_id','user_firebase_token','calender_meeting_id','title','creator','organizer','creation_time','start_time','end_time','attendees_count','meet_link','meet_platform','meeting_description','meeting_location','meeting_transcript','meeting_old_transcript','meeting_audio_file_link','is_multilingual','language','is_summarized','meeting_summary','meeting_old_summary','is_summary_edited','summary_gen_date','reading_time','meeting_category_assigned','model_used','generated_title','topic','top_keywords','top_speaker','roles_detected','top_spent_time_person','decisions','highlights_json','speaker_json','transcript_json','lastModifiedDateTime_microsoft','calendar_platform','is_good','factual_consistency','meeting_summary_old','meeting_duration','meeting_type','sentiments','action_items','risks','assumptions','dependencies','constraints','tradeoffs','questions')
        
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
        fields = ('meeting_id','calender_meeting_id','user_firebase_token','title','creator','organizer','creation_time','start_time','end_time','attendees_count','meet_link','meet_platform','is_summarized')
        
class MicrosoftEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = ('calender_meeting_id','lastModifiedDateTime_microsoft','start_time','end_time','meeting_location','attendees_count','meet_link','calendar_platform','meet_platform','is_summarized')

