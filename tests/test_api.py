import datetime
import json

from flask_testing import TestCase

from api import app, db, Record


class APITestCase(TestCase):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def setUp(self):
        """ setup database and add records """
        db.create_all()

        timestamp = datetime.datetime(
                1999, 9, 9, 9, 9, 9, tzinfo=datetime.timezone.utc
        ).timestamp()

        record = Record(
            timestamp=timestamp,
            temperature=25.0,
            humidity=50.0
        )

        db.session.add(record)
        db.session.commit()

    def tearDown(self):
        """ remove database """
        db.session.remove()
        db.drop_all()

    def create_app(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = self.SQLALCHEMY_DATABASE_URI
        app.config["TESTING"] = self.TESTING
        return app

    def test_delete_record(self):
        response = self.client.delete("/api/records/1")
        self.assert200(response)
        self.assertDictEqual(
            {
                "record": {
                    "timestamp": 936868149.0,
                    "temperature": 25.0,
                    "humidity": 50.0
                },
                "errors": {}
            },
            response.json
        )

    def test_delete_record_404(self):
        response = self.client.delete("/api/records/100")
        self.assert404(response)
        self.assertDictEqual(
            {
                "record": {},
                "errors": {
                    "record_id": "does not exist"
                }
            },
            response.json
        )

    def test_get_record(self):
        response = self.client.get("/api/records/1")
        self.assert200(response)
        self.assertDictEqual(
            {
                "record": {
                    "record_id": 1,
                    "timestamp": 936868149.0,
                    "temperature": 25.0,
                    "humidity": 50.0
                },
                "errors": {}
            },
            response.json
        )

    def test_get_record_404(self):
        response = self.client.get("/api/records/100")
        self.assert404(response)
        self.assertDictEqual(
            {
                "record": {},
                "errors": {
                    "record_id": "does not exist"
                }
            },
            response.json
        )

    def test_get_records_min_timestamp(self):
        response = self.client.get("/api/records?min_timestamp=936868150.0")
        self.assert200(response)
        self.assertDictEqual(
            {
                "records": [],
                "errors": {}
            },
            response.json
        )

        response = self.client.get("/api/records?min_timestamp=936868148.0")
        self.assert200(response)
        self.assertDictEqual(
            {
                "records": [
                    {
                        "record_id": 1,
                        "timestamp": 936868149.0,
                        "temperature": 25.0,
                        "humidity": 50.0
                    },
                ],
                "errors": {}
            },
            response.json
        )

    def test_get_records_max_timestamp(self):
        response = self.client.get("/api/records?max_timestamp=936868148.0")
        self.assert200(response)
        self.assertDictEqual(
            {
                "records": [],
                "errors": {}
            },
            response.json
        )

        response = self.client.get("/api/records?max_timestamp=936868150.0")
        self.assert200(response)
        self.assertDictEqual(
            {
                "records": [
                    {
                        "record_id": 1,
                        "timestamp": 936868149.0,
                        "temperature": 25.0,
                        "humidity": 50.0
                    },
                ],
                "errors": {}
            },
            response.json
        )

    def test_get_records_no_params(self):
        response = self.client.get("/api/records")
        self.assert200(response)
        self.assertDictEqual(
            {
                "records": [
                    {
                        "record_id": 1,
                        "timestamp": 936868149.0,
                        "temperature": 25.0,
                        "humidity": 50.0
                    },
                ],
                "errors": {}
            },
            response.json
        )

    def test_post_record(self):
        response = self.client.post(
            "/api/records",
            data=json.dumps(
                dict(
                    timestamp=500.0,
                    temperature=15.0,
                    humidity=10.0
                )
            ),
            headers={"content-type": "application/json"}
        )
        self.assertStatus(response, 201)
        self.assertDictEqual(
            {
                "record": {
                    "record_id": 2,
                    "timestamp": 500.0,
                    "temperature": 15.0,
                    "humidity": 10.0
                },
                "errors": {}
            },
            response.json
        )

    def test_post_record_invalid_param(self):
        response = self.client.post(
            "/api/records",
            data=json.dumps(
                dict(
                    timestamp=500.0,
                    temperature=15.0,
                    humidity=10.0,
                    precipitation=0.5
                )
            ),
            headers={"content-type": "application/json"}
        )
        self.assertStatus(response, 422)
        self.assertDictEqual(
            {
                "record": {},
                "errors": {
                    "precipitation": ["Unknown field."],
                }
            },
            response.json
        )

    def test_put_record(self):
        response = self.client.put(
            "/api/records/1",
            data=json.dumps(
                dict(
                    timestamp=500.0,
                )
            ),
            headers={"content-type": "application/json"}
        )
        self.assert200(response)
        self.assertDictEqual(
            {
                "record": {
                    "record_id": 1,
                    "timestamp": 500.0,
                    "temperature": 25.0,
                    "humidity": 50.0
                },
                "errors": {}
            },
            response.json
        )

    def test_put_record_404(self):
        response = self.client.put(
            "/api/records/100",
            data=json.dumps(
                dict(
                    timestamp=500.0,
                )
            ),
            headers={"content-type": "application/json"}
        )
        self.assert404(response)
        self.assertDictEqual(
            {
                "record": {},
                "errors": {
                    "record_id": "does not exist"
                }
            },
            response.json
        )

    def test_put_record_no_arguments(self):
        response = self.client.put(
            "/api/records/1",
            headers={"content-type": "application/json"}
        )
        self.assert400(response)
        self.assertDictEqual(
            {"message": "The browser (or proxy) sent a request that this server could not understand."},
            response.json
        )

    def test_validate_max_parameters(self):
        """ validate that temperature and humidity are not too high """
        response = self.client.post(
            "/api/records",
            data=json.dumps(
                dict(
                    timestamp=500.0,
                    temperature=1000.0,
                    humidity=1000.0
                )
            ),
            headers={"content-type": "application/json"}
        )
        self.assertStatus(response, 422)
        self.assertDictEqual(
            {
                "record": {},
                "errors": {
                    "humidity": [
                        "humidity must be between 0 and 100 percent (inclusive)"
                    ]
                },
            },
            response.json
        )

    def test_validate_min_parameters(self):
        """ validate that temperature and humidity are not too low """
        response = self.client.post(
            "/api/records",
            data=json.dumps(
                dict(
                    timestamp=500.0,
                    temperature=-1000.0,
                    humidity=-1000.0
                )
            ),
            headers={"content-type": "application/json"}
        )
        self.assertStatus(response, 422)
        self.assertDictEqual(
            {
                "record": {},
                "errors": {
                    "humidity": [
                        "humidity must be between 0 and 100 percent (inclusive)"
                    ]
                },
            },
            response.json
        )
