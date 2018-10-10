# GOB-Management API

GOB Management API provides a graphql endpoint on process logs.

The endpoint is provided under /graphql

# Requirements

    * docker-compose >= 1.17
    * docker ce >= 18.03
    * python >= 3.6

# Installation

## Local

Create a virtual environment:

    python3 -m venv venv
    source venv/bin/activate
    pip install -r src/requirements.txt

Or activate the previously created virtual environment

    source venv/bin/activate

The API depends on a running management database.
To start a database instance follow the instructions in the GOB-Workflow project.

If GOB-Workflow project has already been initialised then execute:

```bash
    cd ../GOB-Workflow
    docker-compose up management_database &
```

Start the API

```
    cd src
    python -m api
```

The API is exposed at http://127.0.0.1:5000/ when running locally.

### Tests

Testing is not yet available


## Docker

```bash
    docker-compose build
    docker-compose up
```

The API is exposed at http://127.0.0.1:8142/ when running in docker.
