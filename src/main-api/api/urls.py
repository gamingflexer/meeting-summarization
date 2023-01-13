from django.urls import path
from .views import LandingPageAPI

urlpatterns = [
    path('landing', LandingPageAPI.as_view(), name='landing'),
]
