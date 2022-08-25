import re

from flask import jsonify, request
from flask_graphql import GraphQLView
from flask_cors import CORS
from flask_socketio import SocketIO

from gobcore.model import GOBModel
from gobcore.message_broker.notifications import NOTIFY_EXCHANGE
from gobcore.message_broker.config import WORKFLOW_QUEUE

from gobmanagement.config import ALLOWED_ORIGINS, API_BASE_PATH, PUBLIC_API_BASE_PATH
from gobmanagement.app import app
from gobmanagement.database.base import db_session
from gobmanagement.database import get_process_state
from gobmanagement.schemas import schema
from gobmanagement.socket import LogBroadcaster
from gobmanagement.security import SecurityMiddleware

from gobmanagement.jobs import JobHandler

from gobmanagement.message_broker.management import get_queues, purge_queue


def _health():
    return 'Connectivity OK'


def _validate_request(valid_properties, data):
    """Checks if data confirms to valid_properties.

    Valid_properties is a dict with property: regex pairs. Only checks if the data matches the regex when the property
    is not None. None is always valid.

    Also checks if data does not contain any unexpected properties.

    :param valid_properties:
    :param data:
    :return:
    """
    diff = set(data.keys()) - set(valid_properties.keys())

    if diff:
        return [f"Unexpected properties received: {', '.join(diff)}"]

    errors = []
    for property, value in data.items():
        if value is not None and not valid_properties[property].match(value):
            errors.append(f"Invalid format for {property}")
    return errors


def _start_job():
    """
    Start a new job

    The job parameters are contained in the request
    :return:
    """
    alphanumeric = re.compile(r'^\w+$')
    valid_properties = {key: alphanumeric for key in [
        'action', 'catalogue', 'collection', 'destination', 'product', 'attribute', 'mode', 'application',
    ]}
    valid_properties['user'] = re.compile(r'^[\w@(). ]+$')

    data = request.get_json(silent=True)
    errors = _validate_request(valid_properties, data)

    if errors:
        return jsonify({'errors': errors}), 400

    job_handler = JobHandler()
    try:
        msg = job_handler.publish_job(data['action'], data)
        return jsonify(msg['header'])
    except Exception as e:
        # 400 Bad Request
        return f"Job start failed: {str(e)}", 400


def _remove_job(job_id):
    """
    Removes a job

    :param job_id:
    :return:
    """
    job_handler = JobHandler()
    return jsonify(job_handler.remove_job(job_id))


def _catalogs():
    model = GOBModel()
    catalogs = model.get_catalogs()
    result = {}
    for catalog_name, catalog in catalogs.items():
        result[catalog_name] = []
        for entity_name, model in catalog['collections'].items():
            result[catalog_name].append(entity_name)
    return jsonify(result), 200, {'Content-Type': 'application/json'}


CORS(app, origins=ALLOWED_ORIGINS)

_graphql = GraphQLView.as_view(
                'graphql',
                schema=schema,
                graphiql=True  # for having the GraphiQL interface
            )


def _process_state(process_id):
    """
    Returns the state of a process as a list of jobs {id, status}

    This is a whitelisted endpoint. Only the most limited amount of information is returned

    :param process_id:
    :return:
    """
    state = get_process_state(process_id)
    return jsonify(state)


def _workflow_state():
    """
    Return the workflow state as a list of queues {name, #messages_pending}

    Only the queues that start workflows are taken into account

    This is a whitelisted endpoint. Only the most limited amount of information is returned

    :return:
    """
    workflow_queues = [NOTIFY_EXCHANGE, WORKFLOW_QUEUE]
    queues, _ = get_queues()
    state = [{
        'name': queue['name'],
        'messages_unacknowledged': queue['messages_unacknowledged']
    } for queue in [queue for name in workflow_queues for queue in queues if queue['name'].startswith(name)]]
    return jsonify(state)


def _queues():
    queues, status_code = get_queues()
    return jsonify(queues), status_code, {'Content-Type': 'application/json'}


def _queue(queue_name):
    """
    Purge the queue with the specified name

    :param queue_name:
    :return:
    """
    assert request.method == 'DELETE'
    result, status_code = purge_queue(queue_name)
    return jsonify(result), status_code, {'Content-Type': 'application/json'}


security_middleware = SecurityMiddleware(app)

# Routes
ROUTES = [
    # Health check URL
    ('/status/health/', _health, ['GET']),
    (f'{API_BASE_PATH}/job/', _start_job, ['POST']),
    (f'{API_BASE_PATH}/job/<job_id>', _remove_job, ['DELETE']),
    (f'{API_BASE_PATH}/catalogs/', _catalogs, ['GET']),
    (f'{API_BASE_PATH}/graphql/', _graphql, ['GET', 'POST']),
    (f'{API_BASE_PATH}/queues/', _queues, ['GET']),
    (f'{API_BASE_PATH}/queue/<queue_name>', _queue, ['DELETE']),
    # Public URLS
    (f'{PUBLIC_API_BASE_PATH}/state/process/<process_id>', _process_state, ['GET']),
    (f'{PUBLIC_API_BASE_PATH}/state/workflow/', _workflow_state, ['GET'])
]

for route, view_func, methods in ROUTES:
    app.route(rule=route, methods=methods)(view_func)

socketio = SocketIO(app,
                    path=f"{API_BASE_PATH}/socket.io",
                    cors_allowed_origins=ALLOWED_ORIGINS)
logBroadcaster = LogBroadcaster(socketio)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@socketio.on('connect')
def socket_connect():
    logBroadcaster.on_connect()


@socketio.on_error_default
def error_handler(e):
    print('A socket error has occurred: ' + str(e))


@socketio.on('disconnect')
def socket_disconnect():
    logBroadcaster.on_disconnect()
