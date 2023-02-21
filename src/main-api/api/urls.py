from django.urls import path
from .views import LandingPageAPI,AddMeetingAPI,SummaryPagegAPI,AddMeetingFileAPI,EditUserDataAPI
from .calender import GoogleCalendarInitView,GoogleCalendarEventsView,GoogleCalendarRedirectView

urlpatterns = [
    path('landing', LandingPageAPI.as_view(), name='landing'),
    path('addmeeting', AddMeetingAPI.as_view(), name='addmeeting'),
    path('addmeetingfile/<int:meeting_id>', AddMeetingFileAPI.as_view(), name='addmeetingfile'),
    path('summary/<int:meeting_id>', SummaryPagegAPI.as_view(), name='summary'),
    path('userinfo/<str:username>', EditUserDataAPI.as_view(), name='fetch_user_data'),
    path('rest/v1/calendar/init/',
         GoogleCalendarInitView.as_view(), name='calendar_init'),
    path('rest/v1/calendar/redirect/',
         GoogleCalendarRedirectView.as_view(), name='calendar_redirect'),
    path('rest/v1/calendar/events/',
         GoogleCalendarEventsView.as_view(), name='calendar_redirect'),
] 
