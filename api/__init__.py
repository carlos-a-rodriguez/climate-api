import os

from dotenv import load_dotenv
from flask import Flask, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema, validates, ValidationError
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

# SCHEMAS

class RecordSchema(Schema):
    record_id = fields.Int(dump_only=True)
    timestamp = fields.Float(required=True)
    temperature = fields.Float(required=True)
    humidity = fields.Float(required=True)

    @validates("temperature")
    def validate_temperature(self, value):
        if not (-100 <= value <= 100):
            raise ValidationError(
                "temperature must be between -100 and 100 degrees Celcius (inclusive)"
            )

    @validates("humidity")
    def validate_humidity(self, value):
        if not (0 <= value <= 100):
            raise ValidationError(
                "humidity must be between 0 and 100 percent (inclusive)"
            )

record_schema = RecordSchema()
records_schema = RecordSchema(many=True)

# API

class RecordResource(Resource):
    def delete(self, record_id):
        record = Record.query.get(record_id)
        if not record:
            return {"record": {}, "errors": ["record not found"]}, 404
        
        db.session.delete(record)
        db.session.commit()

        # deleted record no longer has a valid record_id
        delete_record_schema = RecordSchema(
            only=("timestamp", "temperature", "humidity")
        )

        return (
            {
                "record": delete_record_schema.dump(record),
                "errors": []
            },
            200
        )

    def get(self, record_id):
        record = Record.query.get(record_id)
        if not record:
            return {"record": {}, "errors": ["record not found"]}, 404
        return (
            {
                "record": record_schema.dump(record),
                "errors": []
            },
            200
        )

    def put(self, record_id):
        return {"method": "PUT"}


class NewRecordResource(Resource):
    def post(self):
        body = request.get_json()

        try:
            data = record_schema.load(body)
        except ValidationError as e:
            return {"record": {}, "errors": e.messages}, 422

        record = Record(**data)

        db.session.add(record)
        db.session.commit()
        db.session.refresh(record)

        return (
            {
                "record": record_schema.dump(record), 
                "errors": []
            },
            201
        )    


api.add_resource(RecordResource, "/record/<int:record_id>")
api.add_resource(NewRecordResource, "/record")
