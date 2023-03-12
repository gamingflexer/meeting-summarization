from django.db import models
from django.utils.timezone import now


# Create your models here.

class User_info(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=255, unique=True)
    user_prof_type = models.CharField(max_length=255, default='SDE')
    user_meeting_category = models.CharField(max_length=255, default='tech')


class Summary(models.Model):  # all meeting data
    meeting_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User_info, on_delete=models.CASCADE)
    calender_meeting_id = models.CharField(unique=True, max_length=70)
    title = models.CharField(max_length=100, null=True, default='')
    creator = models.CharField(max_length=50, null=True, default='')
    organizer = models.CharField(max_length=50, null=True, default='')
    creation_time = models.DateTimeField(null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    attendees_count = models.IntegerField(default=0, null=True)
    meet_link = models.URLField(max_length=200, default='', null=True)
    meet_platform = models.CharField(max_length=10, null=True, default='unknown')
    meeting_description = models.CharField(max_length=255)
    meeting_location = models.CharField(max_length=255)

    meeting_transcript = models.CharField(max_length=10000)
    meeting_audio_file_link = models.CharField(max_length=255)
    is_multilingual = models.BooleanField(default=False)
    language = models.CharField(max_length=255)

    is_summarized = models.BooleanField(default=False, null=False)
    meeting_summary = models.CharField(default="", max_length=3000)  # **Summary**
    summary_gen_date = models.DateField(null=True)
    reading_time = models.CharField(max_length=30)  # in minutes & no of words
    meeting_category_assgined = models.CharField(default="general", max_length=255)
    model_used = models.CharField(max_length=255)

    generated_title = models.CharField(default="", max_length=255)
    topic = models.CharField(max_length=255)
    top_keywords = models.CharField(max_length=255)
    top_speaker = models.CharField(max_length=255)
    roles_detected = models.CharField(max_length=255)
    top_spent_time_person = models.CharField(max_length=255)
    descions = models.CharField(max_length=1000)  # Action Items
    highlights = models.CharField(max_length=5000)

    # Feedbacks
    is_good = models.BooleanField(default=False)
    factual_consistency = models.CharField(max_length=255)
    meeting_summary_old = models.CharField(max_length=200)


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