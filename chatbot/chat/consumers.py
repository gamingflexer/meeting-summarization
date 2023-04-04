import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.views.decorators.csrf import csrf_exempt
import requests
import re

class ChatConsumer(WebsocketConsumer):
    
    @csrf_exempt
    def receive(self, text_data):
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
        try:
            response = requests.post("http://127.0.0.1:3000/api/doc-api", 
                                    data=json.dumps({"query":text_data_json["text"]}), 
                                    headers={"Content-Type": "application/json"})
            response.raise_for_status()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            print("Down")
        except requests.exceptions.HTTPError:
            print("4xx, 5xx")
        res_openai =  (response.json())['data']
        print(res_openai)
        res_openai = re.sub(r'\[.*?\]', '', res_openai)
        res_openai = re.sub(r'[^\w\s]', '', res_openai)
        # We will later replace this call with a celery task that will
        # use a Python library called ChatterBot to generate an automated
        # response to a user's input.
        async_to_sync(self.channel_layer.send)(
            self.channel_name,
            {
                "type": "chat.message",
                "text": {"msg": res_openai, "source": "bot"},
            },
        )

    # Handles the chat.mesage event i.e. receives messages from the channel layer
    # and sends it back to the client.
    def chat_message(self, event):
        text = event["text"]
        self.send(text_data=json.dumps({"text": text}))
