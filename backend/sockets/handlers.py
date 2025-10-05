from app import socketio
from flask_socketio import join_room



@socketio.on("join")
def handle_join(data):
    user_id = str(data.get("room"))
    if user_id:
        join_room(user_id)
        print(f"User joined room: {user_id}")