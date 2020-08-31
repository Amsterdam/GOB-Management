import re

from flask import jsonify, request
from flask_graphql import GraphQLView
from flask_cors import CORS
from flask_socketio import SocketIO

from gobcore.model import GOBModel

from gobmanagement.config import ALLOWED_ORIGINS, API_BASE_PATH
from gobmanagement.app import app
from gobmanagement.database.base import db_session
from gobmanagement.schemas import schema
from gobmanagement.socket import LogBroadcaster
from gobmanagement.auth import RequestUser

from gobmanagement.grpc.services.jobs import JobsServicer

from gobmanagement.message_broker.management import get_queues, purge_queue


def _health():
    return 'Connectivity OK'


def _secure():
    """
    Test endpoint for keycloak
    :return:
    """
    request_user = RequestUser()
    print(request_user)
    return 'Secure access OK'


def _job(job_id=None):
    """
    Create a new job

    :return:
    """
    host = request.host
    runs_locally = "127.0.0.1" in host
    if not runs_locally:
        # External call, check is the caller is authenticated and authorized
        userid = request.headers.get('X-Auth-Userid')
        roles = request.headers.get('X-Auth-Roles', '')
        if userid is None:
            # Check if the user is authenticated => 401 Unauthorized
            return "Not logged in", 401
        elif "gob_adm" not in roles:
            # Check if the user is authorized => 403 Forbidden
            return "Insufficient rights to start job", 403

    if request.method == 'POST':
        return _start_job()
    elif request.method == 'DELETE':
        return _remove_job(job_id)


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
    valid_properties['user'] = re.compile(r'^[\w(). ]+$')

    data = request.get_json(silent=True)
    errors = _validate_request(valid_properties, data)

    if errors:
        return jsonify({'errors': errors}), 400

    jobs_services = JobsServicer()
    try:
        msg = jobs_services.publish_job(data['action'], data)
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
    jobs_services = JobsServicer()
    return jsonify(jobs_services.remove_job(job_id))


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


# Routes
ROUTES = [
    # Health check URL
    ('/status/health/', _health, ['GET']),
    (f'{API_BASE_PATH}/job/', _job, ['POST']),
    (f'{API_BASE_PATH}/job/<job_id>', _job, ['DELETE']),
    (f'{API_BASE_PATH}/catalogs/', _catalogs, ['GET']),
    (f'{API_BASE_PATH}/secure/', _secure, ['GET']),
    (f'{API_BASE_PATH}/graphql/', _graphql, ['GET', 'POST']),
    (f'{API_BASE_PATH}/queues/', _queues, ['GET']),
    (f'{API_BASE_PATH}/queue/<queue_name>', _queue, ['DELETE'])
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
