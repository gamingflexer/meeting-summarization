import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.views.decorators.csrf import csrf_exempt
import requests
import re

class ChatConsumer(WebsocketConsumer):
    
    def connect(self):
        self.meeting_id = self.scope['url_route']['kwargs']['meeting_id']
        self.meeting_id_name = 'chat_%s' % self.meeting_id

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.meeting_id_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.meeting_id_name,
            self.channel_name
        )
    
    @csrf_exempt
    def receive(self, text_data):
        meeting_id = self.scope['url_route']['kwargs']['meeting_id']
        text_data_json = json.loads(text_data)

        # The consumer ChatConsumer is synchronous while the channel layer
        # methods are asynchronous. Therefore wrap the methods in async-to-sync
        async_to_sync(self.channel_layer.send)(
            self.channel_name,
            {
                "type": "chat_message",
                "text": {"msg": text_data_json["text"], "source": "user"},
            },
        )
        
        """GET FROM MEETING DATA"""
        
        try:
            response = requests.get(f"http://127.0.0.1:8000/api/chatbot/summary/{meeting_id}",
                                    headers={"Content-Type": "application/json"})
            response.raise_for_status()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            print("Down")
        except requests.exceptions.HTTPError:
            print("4xx, 5xx")
        
        summary = (response.json())['data']['chatbot_data']['meeting_summary']
        transcript = "sections"
        
        """GET FROM CHATBOT RESPONSE"""
        
        try:
            response = requests.post("http://127.0.0.1:3000/api/chatbot", 
                                    data=json.dumps(
                                                    {"data":
                                                        {"question": text_data_json["text"], 
                                                        "document": summary}}
                                                    ), 
                                    headers={"Content-Type": "application/json"})
            response.raise_for_status()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            print("Down")
        except requests.exceptions.HTTPError:
            print("4xx, 5xx")


        res_openai =  (response.json())['data']
        res_openai = re.sub(r'\[.*?\]', '', res_openai)
        res_openai = re.sub(r'[^\w\s]', '', res_openai)
        
        # We will later replace this call with a celery task that will
        # use a Python library called ChatterBot to generate an automated
        # response to a user's input.
        
        async_to_sync(self.channel_layer.send)(
            self.channel_name,
            {
                "type": "chat.message",
                "text": {"msg": "res_openai", "source": "bot"},
            },
        )

    # Handles the chat.mesage event i.e. receives messages from the channel layer
    # and sends it back to the client.
    def chat_message(self, event):
        text = event["text"]
        self.send(text_data=json.dumps({"text": text}))
