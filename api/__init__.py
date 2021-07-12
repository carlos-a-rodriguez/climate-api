import os

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, MetaData


# SETUP

load_dotenv(".env")

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=naming_convention)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["SQLALCHEMY_DATABASE_URI"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = (
    os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS") == "True"
)
api = Api(app)
db = SQLAlchemy(app, metadata=metadata)

Migrate(app, db)

# MODELS

class Record(db.Model):
    __tablename__ = "records"

    record_id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Float, nullable=False, unique=True)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)

    __table_args__ = (
        CheckConstraint("temperature >= -100 AND temperature <= 100", name="temperature"),
        CheckConstraint("humidity >= 0 AND humidity <= 100", name="humidity")
    )

# API

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
