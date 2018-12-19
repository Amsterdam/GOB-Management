"""__main__

This module is the main module for the API server.

On startup the gobmanagement is instantiated.

"""
from gobmanagement.config import API_PORT
from gobmanagement.api import app, socketio

socketio.run(app=app, port=API_PORT)
