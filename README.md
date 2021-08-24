# climate-api

REST API to add, update and fetch temperature and humidity records from a SQL database.

## basic usage

### setup

Clone the repository:

```shell
$ git clone https://github.com/carlos-a-rodriguez/climate-api.git
$ cd climate-api
```

Add two files to the root directory: `.env` and `.flaskenv`.

Example `.env` file:

```
SQLALCHEMY_DATABASE_URI="<dialect+driver>://<username>:<password>@<host>:<port>/<database>"
SQLALCHEMY_TRACK_MODIFICATIONS=True
```

Replace the value for `SQLALCHEMY_DATABASE_URI` with the appropriate value for your database.

Example `.flaskenv` file:

```
FLASK_APP=api
FLASK_ENV=development
```

Create a virtual environment and install the dependencies:

```shell
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

Apply the migrations to create the database tables:

```shell
$ flask db upgrade
```

If using SQLite, the migrations may fail. This is because SQLite requires "[batch](https://alembic.sqlalchemy.org/en/latest/batch.html)" migrations. If so, you can either update the migrations to use batch operations or delete the migrations and regenerate them.

```shell
$ rm -rf migrations/
$ flask db init
$ flask db migrate -m "initial sqlite migration"
$ flask db upgrade
```

Finally, start the app:

```shell
$ flask run
```

## api

### DELETE /api/records/{record_id}

Remove an existing record from the database.

#### Example

```shell
$ curl -X DELETE http://localhost:5000/api/records/1
```

#### Response

`200 OK`

```json
{
    "record": {
        "timestamp": 936868149.0,
        "temperature": 25.0,
        "humidity": 50.0
    },
    "errors": {}
},
```

### GET /api/records/{record_id}

Get a specific record from the database.

#### Example

```shell
$ curl -X GET http://localhost:5000/api/records/2
```

#### Response

`200 OK`

```json
{
    "errors": {},
    "record": {
        "humidity": 41.0,
        "record_id": 2,
        "temperature": 26.2,
        "timestamp": 1627967578.225778
    }
}
```

### GET /api/records

Get all the records in-between the `min_timestamp` and `max_timestamp`, inclusive.

#### Parameters
- Optional: min_timestamp
    - default: 0
- Optional: max_timestamp
    - default: infinity (i.e. no upper bound)

#### Example

```shell
$ curl -X GET http://localhost:5000/api/records?min_timestamp=1627967030
```

#### Response

`200 OK`

```json
{
    "errors": {},
    "records": [
        {
            "humidity": 44.0,
            "record_id": 1,
            "temperature": 26.4,
            "timestamp": 1627967034.240592
        },
        {
            "humidity": 41.0,
            "record_id": 2,
            "temperature": 26.2,
            "timestamp": 1627967578.225778
        }
    ]
}
```

### PUT /api/records/{record_id}

Update an existing record.

#### Parameters

- Optional: timestamp
    - the timestamp as a float
- Optional: temperature
    - temperature as a float
- Optional: humidity
    - percent humidity as a float between 0 and 100, inclusive

While each of the parameters are optional, at least one must be supplied.

#### Example

```shell
$ curl -X PUT -H "Content-Type: application/json" -d '{"timestamp":1627969263.956442, "temperature":26.1, "humidity":39.0}' localhost:5000/api/records/2
```

#### Response

`200 OK`

```json
{
    "errors": {},
    "record": {
        "humidity": 39.0,
        "record_id": 2,
        "temperature": 26.1,
        "timestamp": 1627969263.956442
    }
}
```

### POST /api/records

Add a new record to the database.

#### Parameters

- Required: timestamp
    - the timestamp as a float
- Required: temperature
    - temperature as a float
- Required: humidity
    - percent humidity as a float between 0 and 100, inclusive

#### Example

```shell
$ curl -X POST -H "Content-Type: application/json" -d '{"timestamp":1627969263.956442, "temperature":26.1, "humidity":39.0}' localhost:5000/api/records
```

#### Response

`200 OK`

```json
{
    "errors": {},
    "record": {
        "humidity": 39.0,
        "record_id": 3,
        "temperature": 26.1,
        "timestamp": 1627969263.956442
    }
}
```

## Errors


### Record Not Found

`GET`, `PUT` and `DELETE` will return a `404 Not Found` if the `record_id` is not in the database.

#### Response

`404 Not Found`

```json
{
    "record": {},
    "errors": {
        "record_id": "does not exist"
    }
},
```

### Invalid Humidity

Humidity is stored as a percent. Any humidity outside of this range will result in a `422 Unprocessable Entity` status code.

#### Response

`422 Unprocessable Entity`

```json
{
    "record": {},
    "errors": {
        "humidity": [
            "humidity must be between 0 and 100 percent (inclusive)"
        ]
    },
},
```

### PUT Without Any Content

To update an existing record, you must submit a change to at least one of the following attributes: `timestamp`, `temperature` or `humidity`. Failure to do so will result in a `400 Bad Request`.

#### Response

`400 Bad Request`

```json
{
    "message": "The browser (or proxy) sent a request that this server could not understand."
}
```
