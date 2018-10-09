from flask_graphql import GraphQLView

from api.app import app
from api.schemas import schema


def _health():
    return 'Connectivity OK'


_graphql = GraphQLView.as_view(
                'graphql',
                schema=schema,
                graphiql=True # for having the GraphiQL interface
            )

# Routes
ROUTES = [
    # Health check URL
    ('/status/health/', _health),
    ('/graphql', _graphql)
]

for route, view_func in ROUTES:
    app.route(rule=route)(view_func)
