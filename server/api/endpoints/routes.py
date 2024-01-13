
from flask_restx import Api, Resource


from .admin.routes import admin_ns as admin_api
from .mentor.routes import mentor_ns as mentor_api
from .mentee.routes import mentee_ns as mentee_api
from .chats.routes import chat_ns as chat_api
from .rtc.routes import webrtc_ns as webrtc_api
from .todos.routes import todos_ns as todos_api

rest_api = Api(title="Mentorship Hub Platform API", version="1.0", doc="/docs", description=" This is a dedicated backend server for student hub mentorship web/mobile app.")

@rest_api.route('/hello')
class HealthCheck(Resource):
    def get(self):
        return {'status': 'healthy'}

                 
rest_api.add_namespace(admin_api)
rest_api.add_namespace(mentor_api)
rest_api.add_namespace(mentee_api)
rest_api.add_namespace(chat_api)
rest_api.add_namespace(webrtc_api)
rest_api.add_namespace(todos_api)

