from django.db import models
from django.utils.timezone import now


# Create your models here.

class User_info(models.Model):
    #user_id = models.AutoField(primary_key=True)
    user_firebase_token = models.CharField(max_length=255, default='', primary_key=True)
    name = models.CharField(max_length=255, default='')
    username = models.CharField(max_length=255, default='')
    email = models.CharField(max_length=255, unique=True)
    user_prof_type = models.CharField(max_length=255, default='SDE')
    user_meeting_category = models.CharField(max_length=255, default='tech')
    onboarding_status = models.BooleanField(default=False)
    calender_onboarding_status = models.BooleanField(default=False)
    
class Summary(models.Model):  # all meeting data
    meeting_id = models.AutoField(primary_key=True)
    user_firebase_token = models.ForeignKey(User_info, on_delete=models.CASCADE, default='')
    calender_meeting_id = models.CharField(max_length=250, null=True, default='')
    
    title = models.CharField(max_length=100, null=True, default='')
    creator = models.CharField(max_length=50, null=True, default='')
    organizer = models.CharField(max_length=50, null=True, default='')
    creation_time = models.DateTimeField(null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    attendees_count = models.IntegerField(default=0, null=True)
    meet_link = models.URLField(max_length=200, default='', null=True, blank=True)
    meet_platform = models.CharField(max_length=10, null=True, default='unknown')
    meeting_description = models.CharField(max_length=255,null=True)
    meeting_location = models.CharField(max_length=255, null=True)

    meeting_transcript = models.CharField(max_length=10000,default = "")
    meeting_old_transcript = models.CharField(max_length=10000,null=True,default=" ")
    meeting_audio_file_link = models.CharField(max_length=255,default="",null=True)
    is_multilingual = models.BooleanField(default=False)
    language = models.CharField(max_length=255,default="",null=True)

    is_summarized = models.BooleanField(default=False, null=False)
    meeting_summary = models.CharField(default="", max_length=3000)  # **Summary**
    meeting_old_summary = models.CharField(default="", max_length=3000)
    is_summary_edited = models.BooleanField(default=False,null=True)
    summary_gen_date = models.DateField(null=True)
    reading_time = models.CharField(max_length=30,default="")  # in minutes & no of words
    meeting_category_assigned = models.CharField(default="general", max_length=255)
    model_used = models.CharField(max_length=255,default="")

    generated_title = models.CharField(default="", max_length=255)
    topic = models.CharField(max_length=255,default="")
    top_keywords = models.CharField(max_length=255,default="")
    top_speaker = models.CharField(max_length=255,default="")
    roles_detected = models.CharField(max_length=255,default="") # JSON DUMP
    top_spent_time_person = models.CharField(max_length=255,default="")
    decisions = models.CharField(max_length=1000,default="")  # Action Items
    
    highlights_json = models.CharField(max_length=5000,default="")
    speaker_json = models.CharField(max_length=5000,default="")
    transcript_json = models.CharField(max_length=6000,default="")
    
    #microsoft
    lastModifiedDateTime_microsoft = models.DateTimeField(null=True,blank=True)
    calendar_platform = models.CharField(null=True,default='Google',max_length=10,blank=True)
    # Feedbacks
    is_good = models.IntegerField(default=0) # 0 --> not rated, 1 --> good, 2 --> bad
    factual_consistency = models.IntegerField(default=0)
    meeting_summary_old = models.CharField(default="", max_length=10000)  # **

    #new
    meeting_duration = models.CharField(max_length=255, null=True)
    meeting_type = models.CharField(max_length=255, null=True)
    sentiments = models.CharField(max_length=100, null=True)
    
    #new + extra
    action_items = models.CharField(max_length=1000, null=True)
    risks = models.CharField(max_length=1000, null=True)
    assumptions = models.CharField(max_length=1000, null=True)
    dependencies = models.CharField(max_length=1000, null=True)
    constraints = models.CharField(max_length=1000, null=True)
    tradeoffs = models.CharField(max_length=1000, null=True)
    questions = models.CharField(max_length=1000, null=True)
    
    
class highlight_template(models.Model):
    user_id = models.ForeignKey(User_info, on_delete=models.CASCADE)
    hightlight_name = models.CharField(max_length=255)
    highlight_desc = models.CharField(max_length=255)
    keywords = models.CharField(max_length=255)
    include_in_summary = models.BooleanField(default=False)


class analytics(models.Model):
    overall_score = models.CharField(max_length=255)  # how much meetings summary is good (0-100) in a pie chart
    # No of meetings per each day js
    particapants_per = models.CharField(max_length=255)  # no of participants in a meetings
    punctuality_per = models.CharField(max_length=255)  # how much meetings are joined on time
    overtime_per = models.CharField(max_length=255)  # how much meetings are going overtime
    sentiment_overall = models.IntegerField()  # how much meetings are good or bad taking SA of the summaries of the meetings
    # Last meetings data per each score SA


class File(models.Model):
    file = models.FileField(blank=False, null=False)
    timestamp = models.DateTimeField(auto_now_add=True)