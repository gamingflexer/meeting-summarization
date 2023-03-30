from flask import Flask, redirect, url_for, session
from flask_socketio import SocketIO, emit
from distutils.log import debug
from flask.helpers import flash
from flask_restful import Api

from decouple import config

from model.retrieval import ChatBot

from utils import set_global_logging_level
import logging
set_global_logging_level(logging.ERROR)

DEBUG = config('DEBUG', cast=bool)
COLLAB = config('COLLAB', cast=bool)

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def create_app():
    # create and configure the app
    app = Flask(__name__)
    socketio = SocketIO(app, cors_allowed_origins="*")
    app.config.from_mapping()
    
    # register views
    from views import app_mbp
    from views.api import IndexPage,AudioApi,SummaryApi,EntitiesApi,ChatApi

    app.register_blueprint(app_mbp)

    api = Api(app, prefix="/api")
    api.add_resource(IndexPage, "/")
    api.add_resource(AudioApi, "/transcript")
    api.add_resource(SummaryApi, "/summarization")
    api.add_resource(EntitiesApi, "/entites")
    api.add_resource(ChatApi, "/chat")
    
    return app, socketio



if __name__ == "__main__":
    app,socketio = create_app()
    
    # Chatbot API's

    # Handle connection from frontend
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')

    # Handle message from frontend
    @socketio.on('message')
    def handle_message(message,transcript,summary):
        chatbot_model,chatbot_tokenizer = chatbot_model_load()
        
        print('Received message: ' + message)
        response = chatbot_response(question = message,
                                    transcript = transcript,
                                    summary = summary,
                                    model = chatbot_model,
                                    tokenizer = chatbot_tokenizer)
        emit('response', response)
        
    
    """ Run app """
    
    if COLLAB and not DEBUG:
        from flask_ngrok import run_with_ngrok
        run_with_ngrok(app)
    if DEBUG:
        socketio.run(app,debug=True)
    if not DEBUG:
        socketio.run(app)