"""__main__

This module is the main module for the API server.

On startup the api is instantiated.

"""
import os

from api.api import app

app.run(port=os.getenv("GOB_MANAGEMENT_PORT", 5001))
