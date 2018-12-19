import os

API_BASE_PATH = "/gob_management"

API_PORT = os.getenv("GOB_MANAGEMENT_PORT", 8143)

ALLOWED_ORIGINS = [
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    "https://acc.iris.data.amsterdam.nl/",
    "https://iris.data.amsterdam.nl/"
]
