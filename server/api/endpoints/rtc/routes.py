from datetime import datetime, timezone, timedelta
import logging, os

from flask import request, url_for, current_app, abort, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource, fields, reqparse
from flask_socketio import SocketIO, emit, send, join_room, leave_room

from ...models.models import ChatConnection, Mentees, Mentors, Community, CommunityMember, Message, User
from ...config import BaseConfig
from ... import socketio


webrtc_ns = Namespace('webrtc', description='WebRTC related operations')

# configure a file handler for admin namespace only
webrtc_ns.logger.setLevel(logging.INFO)
fh = logging.FileHandler("v5.log")
webrtc_ns.logger.addHandler(fh)




@webrtc_ns.route('/test')
class Test(Resource):
    '''Connect test '''

    def get(self):

        return {"success": True, 'message': 'Connection established successfully.'}, HTTPStatus.OK



@socketio.on('connect', namespace='/webrtc_ns')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect', namespace='/webrtc_ns')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('call-student-mentor', namespace='/webrtc_ns')
@jwt_required()
def handle_call_student_mentor(data):
    current_user_id = get_jwt_identity()
    caller = Mentors.query.filter_by(email=current_user_id).first() or Mentees.query.filter_by(email=current_user_id).first()
    room = f"{current_user_id}-{other_user_id}"
    join_room(room)
    emit('incoming-call', {'caller_id': caller.id, 'caller_name': caller.username}, room=room)

@socketio.on('answer-call', namespace='/webrtc_ns')
@jwt_required()
def handle_answer_call(data):
    current_user_id = get_jwt_identity()

    caller_id = data.get('caller_id')
    caller_name = data.get('caller_name')
    accept = data.get('accept')
    room = f"{caller_id}-{current_user_id}"
    join_room(room)
    emit('call-accepted' if accept else 'call-rejected', room=room)

# @socketio.on('call-community', namespace='/webrtc_ns')
# @jwt_required()
# def handle_call_community(data):
#     current_user_id = get_jwt_identity()
#     community_id = data.get('community_id')
#     room = f"community-{community_id}"
    
#     # Check if the current user is a mentor before initiating the call
#     if Mentors.query.filter_by(email=current_user_id).first():
#         room = f"community-{community_id}"
#         join_room(room)
#         emit('incoming-community-call', {'mentor_id': current_user_id}, room=room)
#     else:
#         # You may want to handle the case where a non-mentor tries to initiate a community call
#         emit('call-rejected', {'reason': 'Only mentors can initiate community calls'}, room=request.sid)

#     join_room(room)
#     emit('incoming-community-call', {'mentor_id': current_user_id}, room=room)



from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.models import Mentors, CommunityMember

# ... (previous code remains unchanged)

@socketio.on('call-community', namespace='/webrtc_ns')
@jwt_required()
def handle_call_community(data):
    current_user_id = get_jwt_identity()
    community_id = data.get('community_id')
    room = f"community-{community_id}"

    is_mentor = Mentors.query.filter_by(email=current_user_id).first()
    is_community_member = CommunityMember.query.filter_by(mentor_id=is_mentor.id, community_id=community_id).first() if is_mentor else None

    if is_mentor and is_community_member:
        join_room(room)
        emit('incoming-community-call', {'mentor_id': current_user_id}, room=room)
    else:
        emit('call-rejected', {'reason': 'Only mentors who are community members can initiate community calls'}, room=request.sid)

@socketio.on('answer-community-call', namespace='/webrtc_ns')
@jwt_required()
def handle_answer_community_call(data):
    current_user_id = get_jwt_identity()
    mentor_id = data.get('mentor_id')
    accept = data.get('accept')
    room = f"community-{mentor_id}"


    is_mentor = Mentors.query.filter_by(email=current_user_id).first()
    is_community_member = CommunityMember.query.filter_by(mentor_id=is_mentor.id, community_id=mentor_id).first() if is_mentor else None

    if is_mentor and is_community_member:
        join_room(room)
        emit('community-call-accepted' if accept else 'community-call-rejected', {'receiver_id': current_user_id}, room=room)
    else:
        emit('community-call-rejected', {'reason': 'Only mentors who are community members can answer community calls'}, room=request.sid)


@socketio.on('leave-room', namespace='/webrtc_ns')
def handle_leave_room(data):
    room = data.get('room')
    leave_room(room)
    print(f"Client left room: {room}")


