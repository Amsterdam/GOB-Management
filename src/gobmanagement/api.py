from flask_graphql import GraphQLView
from flask_cors import CORS

from gobmanagement.app import app, socketio
from gobmanagement.database.base import db_session
from gobmanagement.schemas import schema

CORS(app)


def _health():
    return 'Connectivity OK'


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


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

def some_function():
    socketio.emit('some event', {'data': 42})

@socketio.on('connect')
def test_connect():
    print("CONNECT")
    socketio.emit('my response', {'data': 'Connected'})

@socketio.on('disconnect')
def test_disconnect():
    print("DISCONNECT")
    print('Client disconnected')
