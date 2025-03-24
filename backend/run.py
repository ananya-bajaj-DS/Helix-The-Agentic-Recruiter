from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
import eventlet

from app.routes import chat_bp
from app.models import db, UserPreference

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('flask')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

socketio_logger = logging.getLogger('socketio')
socketio_logger.setLevel(logging.DEBUG)
socketio_logger.addHandler(handler)
engineio_logger = logging.getLogger('engineio')
engineio_logger.setLevel(logging.DEBUG)
engineio_logger.addHandler(handler)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, path='/socket.io', cors_allowed_origins="*", logger=True, engineio_logger=True, async_mode='eventlet')

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(chat_bp, url_prefix="/api")

with app.app_context():
    db.create_all()

# Log all incoming requests
@app.before_request
def log_request():
    logger.debug(f"Incoming request: {request.method} {request.path} {request.headers}")

@socketio.on('connect')
def handle_connect():
    token = request.args.get('token')
    logger.debug(f"Token received: {token}")
    if token != 'x063JYBI3N':
        logger.warning("Invalid token, rejecting connection")
        return False  # Reject the connection
    logger.info("Client connected to WebSocket")
    emit('message', {'data': 'Connected to Flask-SocketIO'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info("Client disconnected")

@socketio.on('message')
def handle_message(data):
    logger.info(f"Received message: {data}")
    emit('message', {'data': f"Server received: {data}"}, broadcast=True)

@socketio.on('update_sequence')
def handle_sequence_update(data):
    logger.info(f"Sequence updated: {data}")
    socketio.emit('sequence_updated', data)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)