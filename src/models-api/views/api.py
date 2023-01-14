from werkzeug.utils import secure_filename
from flask_restful import Resource
from flask import request, json
import os

from .models import wav_to_transcript
from utils import allowed_file

from decouple import config

DEBUG = config('DEBUG', cast=bool)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

class AudioApi(Resource):
    def post(self):
        if 'file' not in request.files:
            resp = ({'message' : 'No file part in the request'})
            resp.status_code = 400
            return resp
        file = request.files['file']
        if file.filename == '':
            resp = ({'message' : 'No file selected for uploading'})
            resp.status_code = 400
            return resp
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            result = wav_to_transcript(os.path.join(UPLOAD_FOLDER, filename))
        return {"result": result}, 200
    
class SummaryApi(Resource):
    def get(self):
        return {"result": "summary"}, 200