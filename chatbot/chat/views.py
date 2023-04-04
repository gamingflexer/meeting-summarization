from django.views.generic import TemplateView

class ChatView(TemplateView):

    template_name: str = "chat/chat.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room_name = self.kwargs.get("meeting_id")
        context["meeting_id"] = room_name
        return context