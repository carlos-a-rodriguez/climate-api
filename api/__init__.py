import os

from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema, validates, ValidationError
from sqlalchemy import CheckConstraint, MetaData

# CONSTANTS

RESPONSE_404 = ({"record": {}, "errors": {"record_id": "does not exist"}}, 404)


# SETUP

load_dotenv(".env")

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=naming_convention)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["SQLALCHEMY_DATABASE_URI"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = (
    os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS") == "True"
)
api = Api(app)
db = SQLAlchemy(app, metadata=metadata)

CORS(app)
Migrate(app, db)

# MODELS


class Record(db.Model):
    __tablename__ = "records"

    record_id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Float, nullable=False, unique=True, index=True)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)

    __table_args__ = (
        CheckConstraint("humidity >= 0 AND humidity <= 100", name="humidity"),
    )


# SCHEMAS


class RecordSchema(Schema):
    record_id = fields.Int(dump_only=True)
    timestamp = fields.Float(required=True)
    temperature = fields.Float(required=True)
    humidity = fields.Float(required=True)

    @validates("humidity")
    def validate_humidity(self, value):
        if not (0 <= value <= 100):
            raise ValidationError(
                "humidity must be between 0 and 100 percent (inclusive)"
            )


class QuerySchema(Schema):
    min_timestamp = fields.Float(missing=0)
    max_timestamp = fields.Float(missing=lambda: float("inf"))


query_schema = QuerySchema()
record_schema = RecordSchema()

# API


class RecordResource(Resource):
    def delete(self, record_id):
        record = Record.query.get(record_id)
        if not record:
            return RESPONSE_404

        db.session.delete(record)
        db.session.commit()

        # deleted record no longer has a valid record_id
        delete_record_schema = RecordSchema(
            only=("timestamp", "temperature", "humidity")
        )

        return (
            {
                "record": delete_record_schema.dump(record),
                "errors": {},
            },
            200,
        )

    def get(self, record_id):
        record = Record.query.get(record_id)
        if not record:
            return RESPONSE_404

        return (
            {
                "record": record_schema.dump(record),
                "errors": {},
            },
            200,
        )

    def put(self, record_id):
        record = Record.query.get(record_id)
        if not record:
            return RESPONSE_404

        body = request.get_json()

        try:
            data = record_schema.load(body, partial=True)
        except ValidationError as e:
            return {"record": {}, "errors": e.messages}, 422

        for attr, value in data.items():
            setattr(record, attr, value)

        db.session.add(record)
        db.session.commit()
        db.session.refresh(record)

        return (
            {
                "record": record_schema.dump(record),
                "errors": {},
            },
            200,
        )


class RecordsResource(Resource):
    def get(self):
        try:
            data = query_schema.load(request.args)
        except ValidationError as e:
            return {"records": [], "errors": e.messages}, 422

        records = Record.query.filter(
            data["min_timestamp"] <= Record.timestamp,
            data["max_timestamp"] >= Record.timestamp,
        ).all()

        return (
            {
                "records": record_schema.dump(records, many=True),
                "errors": {},
            },
            200,
        )

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
                "errors": {},
            },
            201,
        )


api.add_resource(RecordResource, "/api/records/<int:record_id>")
api.add_resource(RecordsResource, "/api/records")
