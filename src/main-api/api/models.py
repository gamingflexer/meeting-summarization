from django.db import models

# Create your models here.

class User_info(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=255,unique=True)
    user_prof_type = models.CharField(max_length=255,default='SDE')
    user_meeting_category = models.CharField(max_length=255,default='tech')

class Summary(models.Model):
    meeting_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User_info, on_delete=models.CASCADE)
    scheduled_meeting = models.CharField(max_length=255, null=True)
    scheduled_meeting_time = models.TimeField(blank=True)
    meeting_description = models.CharField(max_length=255)
    meeting_location = models.CharField(max_length=255)
    
    meeting_transcript = models.CharField(max_length=10000)
    meeting_audio_file_link = models.CharField(max_length=255)
    is_multilingual = models.BooleanField(default=False)
    language = models.CharField(max_length=255)
    
    is_summarized = models.BooleanField(default=False,null=False)
    meeting_summary = models.CharField(max_length=200)
    summary_gen_date = models.DateField(null=True)
    reading_time = models.CharField(max_length=30) # in minutes & no of words
    meeting_category_assgined = models.CharField(max_length=255)
    model_used = models.CharField(max_length=255)
    
    
    topic = models.CharField(max_length=255)
    top_keywords = models.CharField(max_length=255)
    top_speaker = models.CharField(max_length=255)
    roles_detected = models.CharField(max_length=255)
    top_spent_time_person = models.CharField(max_length=255)
    descions = models.CharField(max_length=1000) #Action Items
    highlights = models.CharField(max_length=1000)
    
    #Feedbacks
    is_good = models.BooleanField(default=False)
    factual_consistency = models.CharField(max_length=255)
    
    meeting_summary_old = models.CharField(max_length=200)
    
    