from flask_restful import Resource
from flask import request, json

from .models import wav_to_transcript

from decouple import config

DEBUG = config('DEBUG', cast=bool)

class AudioApi(Resource):
    def get(self):
        result = wav_to_transcript("/Users/cosmos/Desktop/Projects/DeepBlue 2/meeting-summarization-api/data/male.wav")
        return {"result": result}, 200
    
class SummaryApi(Resource):
    def get(self):
        return {"result": "summary"}, 200