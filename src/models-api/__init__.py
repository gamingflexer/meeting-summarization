from flask import Flask, redirect, url_for, session
from distutils.log import debug
from flask.helpers import flash
from flask_restful import Api

from decouple import config
import spacy
import os


DEBUG = config('DEBUG', cast=bool)
COLLAB = config('COLLAB', cast=bool)

if not DEBUG:
    import nltk
    nltk.download('wordnet')
    nltk.download('vader_lexicon')
    nltk.download('averaged_perceptron_tagger')
    nlp = spacy.load('en_core_web_lg')
else:
    nlp = spacy.load('en_core_web_sm')


def create_app():
    # create and configure the app
    app = Flask(__name__)
    app.config.from_mapping()
    
    # register views
    from views import app_mbp
    from views.api import AudioApi,SummaryApi,EntitiesApi

    app.register_blueprint(app_mbp)

    api = Api(app, prefix="/api")
    api.add_resource(AudioApi, "/transcript")
    api.add_resource(SummaryApi, "/summarization")
    api.add_resource(EntitiesApi, "/entites")
    
    return app

if __name__ == "__main__":
    app = create_app()
    if COLLAB and not DEBUG:
        from flask_ngrok import run_with_ngrok
        run_with_ngrok(app)
    if DEBUG:
        app.run(debug=True)
    if not DEBUG:
        app.run()