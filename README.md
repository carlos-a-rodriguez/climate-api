# climate-api

REST API to add, update and fetch temperature and humidity records from a SQLite database.

## basic usage

### single record respose (success)

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

**record** is a dictionary.

### multi-record response (success)

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

**records** is a list of dictionaries.

## resources

### DELETE /api/records/{record_id}

```
curl -X DELETE http://localhost:5000/api/records/1
```

### GET /api/records/{record_id}

```
curl -X GET http://localhost:5000/api/records/1
```

### GET /api/records

optional parameters
- min_timestamp
    - default: 0
- max_timestamp
    - default: UTC now

```
curl -X GET http://localhost:5000/api/records?min_timestamp=1627967035
```

### PUT /api/records/{record_id}

```
curl -X PUT -H "Content-Type: application/json" -d '{"timestamp":1627969263.956442, "temperature":26.1, "humidity":39.0}' localhost:5000/api/records/1
```

### POST /api/records

```
curl -X POST -H "Content-Type: application/json" -d '{"timestamp":1627969263.956442, "temperature":26.1, "humidity":39.0}' localhost:5000/api/records
```
