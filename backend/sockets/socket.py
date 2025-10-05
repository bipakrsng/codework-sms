from flask_socketio import SocketIO

# Create socketio instance without app parameter initially
socketio = SocketIO(cors_allowed_origins="*")
