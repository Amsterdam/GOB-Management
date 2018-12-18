from flask_graphql import GraphQLView
from flask_cors import CORS
from flask_socketio import SocketIO

from gobmanagement.app import app
from gobmanagement.database.base import db_session
from gobmanagement.schemas import schema
from gobmanagement.socket import LogBroadcaster


def _health():
    return 'Connectivity OK'


CORS(app)

_graphql = GraphQLView.as_view(
                'graphql',
                schema=schema,
                graphiql=True  # for having the GraphiQL interface
            )

# Routes
ROUTES = [
    # Health check URL
    ('/status/health/', _health),
    ('/gob_management/graphql/', _graphql)
]

for route, view_func in ROUTES:
    app.route(rule=route)(view_func)

socketio = SocketIO(app, path="/gob_management/socket.io", cors_credentials=False)
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
