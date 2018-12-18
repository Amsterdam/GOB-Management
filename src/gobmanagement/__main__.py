"""__main__

This module is the main module for the API server.

On startup the gobmanagement is instantiated.

"""
import os

from gobmanagement.api import app, socketio

socketio.run(app=app, port=os.getenv("GOB_MANAGEMENT_PORT", 8143))
