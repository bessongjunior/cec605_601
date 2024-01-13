from http import HTTPStatus
from datetime import datetime, timezone, timedelta
import logging, os

from flask import request, url_for, current_app, abort, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource, fields, reqparse

from ...models.models import ChatConnection, Mentees, Mentors, Community, CommunityMember, Message, User
from ...config import BaseConfig


chat_ns = Namespace('chats', description='Chat related operations')

# configure a file handler for admin namespace only
chat_ns.logger.setLevel(logging.INFO)
fh = logging.FileHandler("v4.log")
chat_ns.logger.addHandler(fh)



# Model for chat connection request payload
chat_connection_model = chat_ns.model('ChatConnectionModel', {
    'mentor_id': fields.Integer(required=True, description='ID of the mentor to connect with'),
})

# community_chat_model = chat_ns.model('CommunityConnectionModel', {
#     'name': fields.String(required=True, description='Name of the community'),
# })

mentor_join_community_model = chat_ns.model('MentorJoinCommunityModel', {
    'community_id': fields.Integer(required=True, description='ID of the community to join'),
})

mentee_join_community_model = chat_ns.model('MenteeJoinCommunityModel', {
    'community_id': fields.Integer(required=True, description='ID of the community to join'),
})

send_message_model = chat_ns.model('SendMessageModel', {
    'recipient_id': fields.Integer(required=True, description='ID of the message recipient (mentor or mentee)'),
    'content': fields.String(required=True, description='Content of the message'),
})

# Model for representing messages in the response
message_model = chat_ns.model('MessageModel', {
    'id': fields.Integer(description='Message ID'),
    'sender_id': fields.Integer(description='ID of the message sender'),
    'sender_role': fields.String(description='Role of the message sender (mentor or mentee)'),
    'content': fields.String(description='Content of the message'),
    'timestamp': fields.String(description='Timestamp of the message'),
})

community_post_model = chat_ns.model('CommunityPostModel', {
    'community_id': fields.Integer(required=True, description='ID of the community'),
    'content': fields.String(required=True, description='Content of the community post'),
})


@chat_ns.route('/connect')
class ConnectMenteeMentor(Resource):
    '''Connect a student to mentor '''

    @chat_ns.expect(chat_connection_model, validate=True)
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()

        # Assuming the request contains the mentor_id as JSON data
        data = request.get_json()
        mentor_id = data.get('mentor_id')

        # Check if the mentor_id is provided
        if not mentor_id:
            return {'message': 'Mentor ID is required.'}, 400

        # Check if the provided mentor_id exists in the database
        mentor = Mentors.query.get(mentor_id)
        if not mentor:
            return {'message': 'Mentor not found.'}, 404

        # Check if the connection already exists
        existing_connection = ChatConnection.query.filter_by(
            mentee_id=current_user_id,
            mentor_id=mentor_id
        ).first()

        if existing_connection:
            return {'message': 'Connection already exists.'}, 400

        mentee = Mentees.query.get(current_user_id)
        if mentee is None:
            return {'message': 'Only mentees can post in the community.'}, 403

        # Create a new chat connection
        new_connection = ChatConnection(
            mentee_id=mentee.id,
            mentor_id=mentor_id
        )

        # Save the new connection to the database
        db.session.add(new_connection)
        db.session.commit()

        return {"success": True, 'message': 'Connection established successfully.'}, HTTPStatus.CREATED


# Endpoint for a mentor to join a community
@chat_ns.route('/mentor/join')
class MentorJoinCommunity(Resource):
    @jwt_required()
    @chat_ns.expect(mentor_join_community_model, validate=True)
    def post(self):
        current_user_id = get_jwt_identity()

        # Assuming the request contains the community_id in the JSON data
        community_id = request.json.get('community_id')

        # Validate and ensure that the mentor and community exist and are valid
        mentor = Mentors.query.get(current_user_id)
        community = Community.query.get(community_id)

        if not mentor:
            return {'message': 'Mentor not found.'}, 404

        if not community:
            return {'message': 'Community not found.'}, 404

        # Check if the mentor is already a member of the community
        if CommunityMember.query.filter_by(mentor_id=current_user_id, community_id=community_id).first():
            return {'message': 'Mentor is already a member of the community.'}, 400

        # Create a community connection for the mentor
        community_member_mentor = CommunityMember(mentor_id=current_user_id, community_id=community_id)
        db.session.add(community_member_mentor)
        db.session.commit()

        return {"success": True, 'message': 'Mentor joined community successfully.'}, HTTPStatus.OK

# Endpoint for a mentee to join a community
@chat_ns.route('/mentee/join')
class MenteeJoinCommunity(Resource):
    @jwt_required()
    @chat_ns.expect(mentee_join_community_model, validate=True)
    def post(self):
        current_user_id = get_jwt_identity()

        # Assuming the request contains the community_id in the JSON data
        community_id = request.json.get('community_id')

        # Validate and ensure that the mentee and community exist and are valid
        mentee = Mentees.query.get(current_user_id)
        community = Community.query.get(community_id)

        if not mentee:
            return {'message': 'Mentee not found.'}, 404

        if not community:
            return {'message': 'Community not found.'}, 404

        # Check if the mentee is already a member of the community
        if CommunityMember.query.filter_by(mentee_id=current_user_id, community_id=community_id).first():
            return {'message': 'Mentee is already a member of the community.'}, 400

        # Create a community connection for the mentee
        community_member_mentee = CommunityMember(mentee_id=current_user_id, community_id=community_id)
        db.session.add(community_member_mentee)
        db.session.commit()

        return {"success": True, 'message': 'Mentee joined community successfully.'}, HTTPStatus.OK


# Endpoint for a mentor to send a message to a mentor or mentee
@chat_ns.route('/mentor/send-message')
class MentorSendMessage(Resource):

    @jwt_required()
    @chat_ns.expect(send_message_model, validate=True)
    # def post(self):
    #     current_user_id = get_jwt_identity()

    #     # Assuming the request contains the recipient_id and content in the JSON data
    #     recipient_id = request.json.get('recipient_id')
    #     content = request.json.get('content')

    #     # Validate and ensure that the recipient exists and is either a mentor or mentee
    #     recipient = User.query.get(recipient_id)

    #     if not recipient:
    #         return {'message': 'Recipient not found.'}, 404

    #     if not (isinstance(recipient, Mentors) or isinstance(recipient, Mentees)):
    #         return {'message': 'Invalid recipient type.'}, 400

    #     # Create a message
    #     message = Message(sender_id=current_user_id, sender_role='mentee', content=content)

    #     if isinstance(recipient, Mentors):
    #         message.sender_role = 'mentor'
    #         message.mentor = recipient
    #     elif isinstance(recipient, Mentees):
    #         message.sender_role = 'mentee'
    #         message.mentee = recipient

    #     db.session.add(message)
    #     db.session.commit()

    #     return {'message': 'Message sent successfully.'}, 200

    def post(self):
        current_user_id = get_jwt_identity()

        # Assuming the request contains the recipient_id and content in the JSON data
        recipient_id = request.json.get('recipient_id')
        content = request.json.get('content')

        # Check if the recipient is a mentor or mentee
        recipient = Mentors.query.get(recipient_id) or Mentees.query.get(recipient_id)

        if not recipient:
            return {'message': 'Recipient not found.'}, 404

        mentor = Mentors.query.get(current_user_id)
        if mentor is None:
            return {'message': 'Only mentees can post in the community.'}, 403

        # Create a message
        message = Message(sender_id=mentor.id, sender_role='mentor', content=content, recipient_id=recipient_id)

        db.session.add(message)
        db.session.commit()

        return {'message': 'Message sent successfully.'}, HTTPStatus.OK


# Endpoint for a mentee to send a message to a mentor or mentee
@chat_ns.route('/mentee/send-message')
class MenteeSendMessage(Resource):
    @jwt_required()
    @chat_ns.expect(send_message_model, validate=True)
    def post(self):
        current_user_id = get_jwt_identity()

        # Assuming the request contains the recipient_id and content in the JSON data
        recipient_id = request.json.get('recipient_id')
        content = request.json.get('content')

        mentee = Mentees.query.get(current_user_id)
        if mentee is None:
            return {'message': 'Only mentees can post in the community.'}, 403

        # Check if the recipient is a mentor or mentee
        recipient = Mentors.query.get(recipient_id) or Mentees.query.get(recipient_id)

        if not recipient:
            return {'message': 'Recipient not found.'}, 404

        # Create a message
        message = Message(sender_id=mentee.id, sender_role='mentee', content=content, recipient_id=recipient_id)

        db.session.add(message)
        db.session.commit()

        return {'message': 'Message sent successfully.'}, HTTPStatus.OK



# Endpoint for a mentor to post in the community
@chat_ns.route('/community/mentor/post')
class MentorPostInCommunity(Resource):
    @jwt_required()
    @chat_ns.expect(community_post_model, validate=True)
    def post(self):
        current_user_id = get_jwt_identity()

        # Extract community_id and content from the request
        community_id = request.json.get('community_id')
        message_content = request.json.get('content')

        mentor = Mentors.query.get(current_user_id)
        if mentor is None:
            return {'message': 'Only mentees can post in the community.'}, 403

        # Create a message for posting in the community
        new_message = Message(sender_id=mentor.id, sender_role='mentor', content=message_content, community_id=community_id)
        db.session.add(new_message)
        db.session.commit()

        return {'message': 'Message posted in community successfully.'}, 200

# Endpoint for a mentee to post in the community
@chat_ns.route('/community/mentee/post')
class MenteePostInCommunity(Resource):
    @jwt_required()
    @chat_ns.expect(community_post_model, validate=True)
    def post(self):
        current_user_id = get_jwt_identity()


        # Extract community_id and content from the request
        community_id = request.json.get('community_id')
        message_content = request.json.get('content')

        mentee = Mentees.query.get(current_user_id)
        if mentee is None:
            return {'message': 'Only mentees can post in the community.'}, 403

        # Create a message for posting in the community
        new_message = Message(sender_id=mentee.id, sender_role='mentee', content=message_content, community_id=community_id)
        db.session.add(new_message)
        db.session.commit()

        return {'message': 'Message posted in community successfully.'}, 200









# Endpoint to get all messages
# @chat_ns.route('/messages')
# class GetMessages(Resource):
#     @jwt_required()
#     @chat_ns.marshal_with(message_model, as_list=True)
#     def get(self):
#         current_user_id = get_jwt_identity()

#         # Get all messages sent or received by the current user, ordered by timestamp
#         messages = Message.query.filter(or_(Message.sender_id == current_user_id, Message.recipient_id == current_user_id)).order_by(Message.timestamp).all()

#         return messages, HTTPStatus.OK
# Endpoint to get all messages
@chat_ns.route('/messages')
class GetAllMessages(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()

        # Assuming you have a model for your UI representation
        class MessageUIModel:
            def __init__(self, sender_id, sender_name, content, timestamp):
                self.sender_id = sender_id
                self.sender_name = sender_name
                self.content = content
                self.timestamp = timestamp

        # Query all messages where the current user is the sender or recipient
        messages = Message.query.filter(or_(Message.sender_id == current_user_id, Message.recipient_id == current_user_id)).all()

        # Format the messages for UI display
        formatted_messages = []

        for message in messages:
            sender_name = Mentors.query.get(message.sender_id).username if message.sender_role == 'mentor' else Mentees.query.get(message.sender_id).username
            formatted_message = MessageUIModel(sender_id=message.sender_id, sender_name=sender_name, content=message.content, timestamp=message.timestamp)
            formatted_messages.append(formatted_message)

        return {'messages': [message.__dict__ for message in formatted_messages]}, HTTPStatus.OK




# Endpoint to get all community messages
@chat_ns.route('/community/messages')
class GetAllCommunityMessages(Resource):
    @jwt_required()
    @chat_ns.marshal_with(message_model, as_list=True)
    def get(self):
        current_user_id = get_jwt_identity()

        # Get all community messages for the communities the user belongs to, ordered by timestamp
        community_messages = Message.query.filter_by(sender_id=current_user_id).order_by(Message.timestamp).all()

        return community_messages, 200
