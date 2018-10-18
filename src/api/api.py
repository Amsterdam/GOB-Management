from flask_graphql import GraphQLView

from api.app import app
from api.database.base import db_session
from api.schemas import schema


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
