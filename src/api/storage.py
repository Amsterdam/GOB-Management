from sqlalchemy.engine.url import URL
from flask_sqlalchemy import SQLAlchemy

from api.config import GOB_MANAGEMENT_DB
from api.app import app

# Configs
uri = URL(**GOB_MANAGEMENT_DB)
app.config['SQLALCHEMY_DATABASE_URI'] = uri

# Modules
db = SQLAlchemy(app)
