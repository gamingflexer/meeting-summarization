from django.urls import path
from .views import LandingPageAPI,AddMeetingAPI

urlpatterns = [
    path('landing', LandingPageAPI.as_view(), name='landing'),
    path('addmeeting', AddMeetingAPI.as_view(), name='addmeeting'),
]
