from flask import jsonify, request
from flask_graphql import GraphQLView
from flask_cors import CORS
from flask_socketio import SocketIO

from gobmanagement.config import ALLOWED_ORIGINS, API_BASE_PATH
from gobmanagement.app import app
from gobmanagement.database.base import db_session, session_scope
from gobmanagement.schemas import schema
from gobmanagement.socket import LogBroadcaster
from gobmanagement.auth import RequestUser

from gobmanagement.grpc.services.jobs import JobsServicer


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


@app.route(f'{API_BASE_PATH}/job/', methods=['POST'])
def _job():
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

    data = request.get_json(silent=True)

    jobs_services = JobsServicer()
    try:
        msg = jobs_services.publish_job(data['action'], data)
        return jsonify(msg['header'])
    except Exception as e:
        # 400 Bad Request
        return f"Job start failed: {str(e)}", 400


def create_session_middleware(session_backend=session_scope):
    def session_middleware(next, root, info, **args):
        with session_backend() as session:
            info.context = dict(
                session=session
            )
        return next(root, info, **args)
    return session_middleware


CORS(app, origins=ALLOWED_ORIGINS)

_graphql = GraphQLView.as_view(
                'graphql',
                schema=schema,
                middleware=[create_session_middleware()],
                graphiql=True  # for having the GraphiQL interface
            )


# Routes
ROUTES = [
    # Health check URL
    ('/status/health/', _health),
    (f'{API_BASE_PATH}/secure/', _secure),
    (f'{API_BASE_PATH}/graphql/', _graphql)
]

for route, view_func in ROUTES:
    app.route(rule=route)(view_func)

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
