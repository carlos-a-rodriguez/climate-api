from flask import Flask
from flask_restful import Api, Resource


app = Flask(__name__)
api = Api(app)


class Record(Resource):
    def delete(self, record_id):
        return {"method": "DELETE"}

    def get(self, record_id):
        return {"method": "GET"}

    def put(self, record_id):
        return {"method": "PUT"}


class NewRecord(Resource):
    def post(self):
        return {"method": "POST"}


api.add_resource(Record, "/record/<int:record_id>")
api.add_resource(NewRecord, "/record")
