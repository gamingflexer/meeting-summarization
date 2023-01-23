from distutils.log import debug
from flask import Flask, redirect, url_for, session
from flask.helpers import flash
from flask_restful import Api
import os

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
    app.run(debug=True)