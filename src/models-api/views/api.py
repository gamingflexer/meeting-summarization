from flask_restful import Resource
from flask import request, json

class TestApi(Resource):
    def get(self, id):
        print("GET", id)
        return {"id": id}, 200