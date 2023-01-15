from django.urls import path
from .views import LandingPageAPI,AddMeetingAPI,SummaryPagegAPI,AddMeetingFileAPI

urlpatterns = [
    path('landing', LandingPageAPI.as_view(), name='landing'),
    path('addmeeting', AddMeetingAPI.as_view(), name='addmeeting'),
    path('addmeetingfile/<int:meeting_id>', AddMeetingFileAPI.as_view(), name='addmeetingfile'),
    path('summary/<int:meeting_id>', SummaryPagegAPI.as_view(), name='summary')
] 