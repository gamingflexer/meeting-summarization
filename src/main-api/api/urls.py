from django.urls import path

from .views import LandingPageAPI,AddMeetingAPI,SummaryPageAPI,AddMeetingFileAPI,EditUserDataAPI,FeedBackAPI,OnboardingAPI,DownloadpdfAPI,AnalyticsAPI,StartSummarization,ChatbotAPI

from .calender import GoogleCalendarInitView,GoogleCalendarEventsView,GoogleCalendarRedirectView,GoogleCalendarMultipleEventsView
from .microsoftauth import MicrosoftCalendarInitView, MicrosoftCallback,MicrosoftEvent

urlpatterns = [
    # Landing Page API
    path('onboarding', OnboardingAPI.as_view(), name='onboarding'),
    path('landing', LandingPageAPI.as_view(), name='landing'),

    # Meetings API
    path('addmeeting', AddMeetingAPI.as_view(), name='addmeeting'),
    path('addmeetingfile/<int:meeting_id>', AddMeetingFileAPI.as_view(), name='addmeetingfile'),

    # Summary API    
    path('userinfo/<str:username>', EditUserDataAPI.as_view(), name='fetch_user_data'),
    path('summary/<int:meeting_id>', SummaryPageAPI.as_view(), name='summary'), # Edit summary also in this
    path('summary/<int:meeting_id>/start', StartSummarization.as_view(), name='summary_start'),
    path('summary/<int:meeting_id>/pdf', DownloadpdfAPI.as_view(), name='summary_pdf'),
    path('summary/feedback/<int:meeting_id>/<str:param>/<int:val>', FeedBackAPI.as_view(), name='summary_feedback'), #is_good #factual_consistency

    # Google Calendar API
    path('rest/v1/calendar/init/', GoogleCalendarInitView.as_view(), name='calendar_init'),
    path('rest/v1/calendar/redirect/', GoogleCalendarRedirectView.as_view(), name='calendar_redirect'),
    path('rest/v1/calendar/events/', GoogleCalendarEventsView.as_view(), name='calendar_redirect'),
    path('meetings-data/<api_keyword>', GoogleCalendarMultipleEventsView.as_view(), name='calendar_upcoming_event'),

    # User API
    path('userinfo', EditUserDataAPI.as_view(), name='fetch_user_data'),
    
    # Analytics API
    path('analytics/<user_id>', AnalyticsAPI.as_view(), name='analytics'),

    path('microsoft_login/', MicrosoftCalendarInitView.as_view(), name='microsoft_login'),
    path('microsoft_callback/', MicrosoftCallback.as_view(), name='microsoft_callback'),
    path('get_microsoft_event/', MicrosoftEvent.as_view(), name='get_microsoft_event'),
    # path('editsummary/<int:meeting_id>',EditSummaryAPI.as_view(),name = 'edit_summary')
    
    #Chatbot API
    path('chatbot/<summary>/<int:meeting_id>', ChatbotAPI.as_view(), name='chatbot'),

] 
