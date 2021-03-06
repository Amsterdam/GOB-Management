# GOB-Management

Provides for an API to monitor and manage GOB

# Docker

## Requirements

* docker-compose >= 1.17
* docker ce >= 18.03
    
## Run

```bash
docker-compose build
docker-compose up &
```

The API is exposed at port 8143 (http://localhost:8143/gob_management/graphql/)

## Tests

```bash
docker-compose -f src/.jenkins/test/docker-compose.yml build
docker-compose -f src/.jenkins/test/docker-compose.yml run --rm test
```

# Local

## Requirements

* python >= 3.6
    
## Initialisation

Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r src/requirements.txt
```
    
Or activate the previously created virtual environment

```bash
source venv/bin/activate
```

Build gRPC code

```
cd src
./build.sh
```
    
# Run

Start the service:

```bash
cd src
python -m gobmanagement
```

The API is exposed at port 8143 (http://localhost:8143/gob_management/graphql/)

## Tests

Run the tests:

```bash
cd src
sh test.sh
```

# Security

Access to GOB Management can be protected by using gatekeeper.

The configuration variables can be stored in .env.
An example configuration can be found in .env.example.

Gatekeeper is bypassed for local development.
To activate gatekeeper for local development please follow the directions specified in docker-compose.yml.

# GraphQL

GOB Management API provides a graphql endpoint on process logs.

The endpoint is provided under /graphql

The logs can be queried using the following examples:

```
{
  logs {
    edges {
      node {
        processId
        timestamp
        msg
      }
    }
  }
}
```

To filter the logs on a single process_id use the following example
(replace PROCESSID with an actual value):

```
{
  logs(processId: "PROCESSID") {
    edges {
      node {
        processId
        timestamp
        msg
      }
    }
  }
}
```

To filter the logs on a source-entity combination use the following example:

```
{
  logs(source: "Grondslag" entity: "meetbouten") {
    edges {
      node {
        processId
        timestamp
        msg
      }
    }
  }
}
```

To get a list of all possible source-entity combinations use:
```
{
  sourceEntities {
    source
    entity
  }
}
```
