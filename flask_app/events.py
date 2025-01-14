from flask_socketio import emit, join_room, leave_room
from flask import request
from . import socketio
from flask import session

@socketio.on('join_board')
def on_join(data):
    print("Join board event received:", data)  # Debug log
    board_id = data.get('board_id')
    room = f"board_{board_id}"
    user_email = session.get('email')
    
    print(f"Session email: {user_email}")  # Debug log
    print(f"Room name: {room}")  # Debug log
    
    join_room(room)
    
    # Emit join message to all users in the room
    join_data = {
        'user_email': user_email,
        'board_id': board_id
    }
    print("Emitting user_joined with data:", join_data)  # Debug log
    
    emit('user_joined', join_data, room=room)

@socketio.on('leave_board')
def on_leave(data):
    board_id = data['board_id']
    room = f"board_{board_id}"
    leave_room(room)
    print(f"Client left board {board_id}")

@socketio.on('card_moved')
def handle_card_move(data):
    board_id = data['board_id']
    room = f"board_{board_id}"
    emit('card_moved', data, room=room, include_self=False)

@socketio.on('card_updated')
def handle_card_update(data):
    board_id = data['board_id']
    room = f"board_{board_id}"
    emit('card_updated', data, room=room, include_self=False)

@socketio.on('card_deleted')
def handle_card_delete(data):
    board_id = data['board_id']
    room = f"board_{board_id}"
    emit('card_deleted', data, room=room, include_self=False)

@socketio.on('card_created')
def handle_card_create(data):
    board_id = data['board_id']
    room = f"board_{board_id}"
    emit('card_created', data, room=room, include_self=False)

@socketio.on('card_editing_started')
def handle_card_editing_started(data):
    board_id = data['board_id']
    room = f"board_{board_id}"
    emit('card_locked', data, room=room, include_self=False)

@socketio.on('card_editing_finished')
def handle_card_editing_finished(data):
    board_id = data['board_id']
    room = f"board_{board_id}"
    emit('card_unlocked', data, room=room, include_self=False)

@socketio.on('send_message')
def handle_message(data):
    print('Message received:', data)  # Debug log
    emit('new_message', {
        'msg': data['msg'],
        'user': session.get('email', 'Anonymous')
    }, broadcast=True)

@socketio.on('joined')
def handle_join(data):
    board_id = data.get('board_id')
    room = f"board_{board_id}"
    user_email = session.get('email', 'Anonymous')
    
    join_room(room)
    emit('status_update', {
        'msg': f'{user_email} has joined the chat.',
        'style': 'status'
    }, room=room) 