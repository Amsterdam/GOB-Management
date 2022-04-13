"""Configuration

The API configuration consists of the specification of the storage (GOB_DB)
and the specification of the model (get_gobmodel)

"""
import os

GOB_MANAGEMENT_DB = {
    'drivername': 'postgresql',
    'database': "gob_management",
    'username': os.getenv("DATABASE_USER", "gob"),
    'password': os.getenv("DATABASE_PASSWORD", "insecure"),
    'host': os.getenv("DATABASE_HOST_OVERRIDE", "localhost"),
    'port': os.getenv("DATABASE_PORT_OVERRIDE", 5407),
}
