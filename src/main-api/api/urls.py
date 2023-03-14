from django.urls import path

from .views import LandingPageAPI,AddMeetingAPI,SummaryPageAPI,AddMeetingFileAPI,EditUserDataAPI,FeedBackAPI,EditSummaryAPI
from .calender import GoogleCalendarInitView,GoogleCalendarEventsView,GoogleCalendarRedirectView,GoogleCalendarMultipleEventsView
from .microsoftauth import microsoft_login, microsoft_callback

urlpatterns = [
    # Landing Page API
    path('landing', LandingPageAPI.as_view(), name='landing'),

    # Meetings API
    path('addmeeting', AddMeetingAPI.as_view(), name='addmeeting'),
    path('addmeetingfile/<int:meeting_id>', AddMeetingFileAPI.as_view(), name='addmeetingfile'),

    # Summary API
    path('summary/<int:meeting_id>', SummaryPageAPI.as_view(), name='summary'),
    path('userinfo/<str:username>', EditUserDataAPI.as_view(), name='fetch_user_data'),
    path('summary/<int:meeting_id>', SummaryPageAPI.as_view(), name='summary'),
    path('summary/<int:meeting_id>/pdf', SummaryPageAPI.as_view(), name='summary_pdf'),
    
    path('summary/feedback/<int:meeting_id>/<str:param>', FeedBackAPI.as_view(), name='summary_feedback'), #is_good #factual_consistency

    # Google Calendar API
    path('rest/v1/calendar/init/',
         GoogleCalendarInitView.as_view(), name='calendar_init'),
    path('rest/v1/calendar/redirect/',
         GoogleCalendarRedirectView.as_view(), name='calendar_redirect'),
    path('rest/v1/calendar/events/',
         GoogleCalendarEventsView.as_view(), name='calendar_redirect'),
    path('summary/<int:meeting_id>', SummaryPageAPI.as_view(), name='summary'),
    path('summary/<int:meeting_id>/pdf', SummaryPageAPI.as_view(), name='summary_pdf'),
    path('userinfo/<str:username>', EditUserDataAPI.as_view(), name='fetch_user_data'),
    path('calendar/multipleevents/<api_keyword>',
         GoogleCalendarMultipleEventsView.as_view(), name='calendar_upcoming_event'),

    # User API
    path('userinfo/<str:username>', EditUserDataAPI.as_view(), name='fetch_user_data'),

    path('microsoft_login/', microsoft_login, name='microsoft_login'),
    path('microsoft_callback/', microsoft_callback, name='microsoft_callback'),
    path('editsummary/<int:meeting_id>',EditSummaryAPI.as_view(),name = 'edit_summary')

] 
