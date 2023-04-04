
from django.urls import path
from .views import ChatView

app_name = "chat"

urlpatterns = [path("<int:meeting_id>/", ChatView.as_view(), name="chat_view")]
