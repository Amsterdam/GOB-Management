from flask import Flask
from flask_socketio import SocketIO

# app initialization
app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_credentials=False, cors_allowed_origins="http://localhost:8080")
