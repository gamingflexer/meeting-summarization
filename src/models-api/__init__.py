from distutils.log import debug
from flask import Flask, redirect, url_for, session
from flask.helpers import flash
from flask_restful import Api
from datetime import datetime
from decouple import config

def create_app():
    # create and configure the app
    app = Flask(__name__)
    app.config.from_mapping()

    # register views
    from views import app_mbp
    from views.api import TestApi

    app.register_blueprint(app_mbp)

    api = Api(app, prefix="/api")
    api.add_resource(TestApi, "/test/<string:id>")
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)