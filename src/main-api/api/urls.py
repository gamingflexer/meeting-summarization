from django.urls import path
from .views import LandingPageAPI,AddMeetingAPI,SummaryPageAPI,AddMeetingFileAPI,EditUserDataAPI

urlpatterns = [
    path('landing', LandingPageAPI.as_view(), name='landing'),
    path('addmeeting', AddMeetingAPI.as_view(), name='addmeeting'),
    path('addmeetingfile/<int:meeting_id>', AddMeetingFileAPI.as_view(), name='addmeetingfile'),
    path('summary/<int:meeting_id>', SummaryPageAPI.as_view(), name='summary'),
    path('summary/<int:meeting_id>/pdf', SummaryPageAPI.as_view(), name='summary_pdf'),
    path('userinfo/<str:username>', EditUserDataAPI.as_view(), name='fetch_user_data')
] 
