from flask_graphql import GraphQLView
from flask_cors import CORS
from flask_socketio import SocketIO

from gobmanagement.config import ALLOWED_ORIGINS, API_BASE_PATH
from gobmanagement.app import app
from gobmanagement.database.base import db_session
from gobmanagement.schemas import schema
from gobmanagement.socket import LogBroadcaster


def _health():
    return 'Connectivity OK'


def _secure():
    """
    Test endpoint for keycloak
    :return:
    """
    return 'Secure access OK'


CORS(app, origins=ALLOWED_ORIGINS)

_graphql = GraphQLView.as_view(
                'graphql',
                schema=schema,
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
