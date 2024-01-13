
from datetime import datetime, timezone, timedelta
import logging, os, imghdr
from functools import wraps
from http import HTTPStatus

from flask import request, url_for, current_app, abort, send_from_directory
from flask_restx import Namespace, Resource, fields, reqparse
from flask_jwt_extended import create_access_token, get_jwt_identity,jwt_required
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
# import httpx



from ...models.models import db, Mentees, JWTTokenBlocklist
from ...config import BaseConfig
# import requests

mentee_ns = Namespace('mentee', description='Mentee operations')

# configure a file handler for admin namespace only
mentee_ns.logger.setLevel(logging.INFO)
fh = logging.FileHandler("v2.log")
mentee_ns.logger.addHandler(fh)

# Flask-Restx schema models for api request and response data
parser = reqparse.RequestParser()

upload_parser = mentee_ns.parser()

upload_parser.add_argument('profile_picture', 
                           location='files', 
                           type = FileStorage, 
                           required=True, 
                        #    action='append'
                        )

mentee_signup_model = mentee_ns.model('MenteeSignUpModel', {
                                            "fullname": fields.String(required=True, min_length=2, max_length=32),
                                            "matricule": fields.String(required=True, min_length=2, max_length=32),
                                            "username": fields.String(required=True, min_length=2, max_length=32),
                                            "email": fields.String(required=True, min_length=4, max_length=64),
                                            "password": fields.String(required=True, min_length=6, max_length=16),
                                            "department": fields.String(required=True, min_length=3, max_length=32),
                                        })

mentee_login_model = mentee_ns.model('MenteeLoginModel', {
                                        "email": fields.String(required=True, min_length=4, max_length=64),
                                        "password": fields.String(required=True, min_length=4, max_length=16)
                                        })

mentee_edit_model = mentee_ns.model('MenteeEditModel', {"userID": fields.String(required=True, min_length=1, max_length=32),
                                                   "username": fields.String(required=True, min_length=2, max_length=32),
                                                   "email": fields.String(required=True, min_length=4, max_length=64)
                                                   })

# Helper function for JWT token required

allowed_extensions = set(['jpg', 'png', 'jpeg', 'gif'])

def allowed_file(filename):
    '''check if the file name has our valide extension'''
    for filetype in allowed_extensions:
        return filetype
    # return filetype in allowed_extensions

def validate_image(stream):
    header = stream.read(512)
    stream.seek(0) 
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

# Flask-Restx routes



@mentee_ns.route('/v1/auth/register')
class Register(Resource):
    """
       Creates a new mentee by taking 'mentee_signup_model' input
    """

    @mentee_ns.expect(mentee_signup_model, validate=True)
    def post(self):

        req_data = request.get_json()

        _username = req_data.get("username")
        _fullname = req_data.get("fullname")
        _matricule = req_data.get("matricule")
        _email = req_data.get("email")
        _password = req_data.get("password")
        _department = req_data.get("department")

        mentee_exists = Users.get_by_email(_email)
        if mentee_exists:
            # add log
            return {"success": False,
                    "msg": "Email already taken"}, HTTPStatus.BAD_REQUEST

        new_mentee = Mentees(
            username=_username, 
            fullnamee=_fullname,
            matricule=_matricule,
            email=_email,
            department=_department
            )

        new_mentee.set_password(_password)
        new_mentee.save()

        return {"success": True,
                "userID": new_mentee.id,
                "msg": "The user was successfully registered"}, HTTPStatus.CREATED


@mentee_ns.route('/v1/auth/login')
class Login(Resource):
    """
       Login mentee by taking 'mentee_login_model' input and return JWT token
    """

    @mentee_ns.expect(mentee_login_model, validate=True)
    def post(self):

        req_data = request.get_json()

        _email = req_data.get("email")
        _password = req_data.get("password")

        mentee_exists = Users.get_by_email(_email)

        if not mentee_exists:
            return {"success": False,
                    "msg": "This email does not exist."}, HTTPStatus.BAD_REQUEST

        if not mentee_exists.check_password(_password):
            return {"success": False,
                    "msg": "Wrong credentials."}, HTTPStatus.BAD_REQUEST

        # create access token uwing JWT
        token = jwt.encode({'email': _email, 'exp': datetime.utcnow() + timedelta(minutes=30)}, BaseConfig.SECRET_KEY)

        mentee_exists.set_jwt_auth_active(True)
        mentee_exists.save()

        access_token = create_access_token(identity=_email, expires_delta=timedelta(minutes=45))

        image_url = url_for('static', filename=f'profile/{mentee_exists.profile_photo}', _external=True)

        return {"success": True,
                "token": access_token,
                "user": mentee_exists.toJSON(),
                "image_url": image_url
                }, HTTPStatus.CREATED


@mentee_ns.route('/v1/mentee/edit')
class EditUser(Resource):
    """
       Edits Mentee's username or password or both using 'mentee_edit_model' input
    """

    @mentee_ns.expect(mentee_edit_model)
    @jwt_required
    def patch(self, current_user):

        req_data = request.get_json()

        _new_menteename = req_data.get("username")
        _new_email = req_data.get("email")

        if _new_menteename:
            self.update_username(_new_menteename)

        if _new_email:
            self.update_email(_new_email)

        self.save()

        return {"success": True, 'msg': 'updated was successful'}, HTTPStatus.ACCEPTED
    

    @mentee_ns.expect(upload_parser)
    @jwt_required
    def put(self, current_user): #
        '''Upload profile picture'''

        args = upload_parser.parse_args()
        file = args['profile_picture']

        current_user = get_jwt_identity()
        mentee_updates = Admin.query.filter_by(email=current_user).first()

        # mentee_updates = Users.query.filter_by(id=int(current_user)).first() #current_user._id # replace with the technique bove
        
        if file is None:
                # add logs
                return {"success": False, "msg": "Field not found, please resend!"}, HTTPStatus.NO_CONTENT #401
        
        if mentee_updates is None:
                # add logs
                return{"success": False, "msg":"The param 'id' mismatch"}, HTTPStatus.BAD_REQUEST #401
        
        
        if not allowed_file(file.filename):
                # add logs 
                return {'success': False, 'msg': 'file type not accepted'}, HTTPStatus.FORBIDDEN
        path = os.path.join(current_app.config['UPLOAD_PICTURE'], str(current_user._id))
        # path = os.path.join(current_app.config['UPLOAD_PICTURE'], "1")
        if not os.path.exists(path):
            os.makedirs(path)
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1]
        if allowed_file(file.filename) or file_ext != validate_image(file.stream):
                # filename = secure_filename(file.filename)
                # print(filename)
                # double checking the file type.
                # if filename != '':
                    # file_ext = os.path.splitext(filename)[1]
            if file_ext not in current_app.config['UPLOAD_EXTENSIONS'] or file_ext != validate_image(file.stream):
                abort(400)
                # add logs
                # return{}, 400
            file.save(os.path.join(path, filename))

        mentee_updates.profile_photo = filename
        db.session.commit()

        return {"success": True,
                "msg": "Image uploaded with success" }, HTTPStatus.ACCEPTED   


@mentee_ns.route('/v1/auth/logout')
class LogoutUser(Resource):
    """
       Logs out Mentee using 'Mentee_logout_model' input
    """

    @jwt_required
    def post(self, current_user):

        _JWT_token = request.headers.get('Authorization')
        # _jwt_token = request.headers["authorization"]
        current_mentor = get_jwt_identity()

        mentor_checked = Mentors.get_by_id(current_mentor)
        print(mentor_checked)
        mentor_checked.set_jwt_auth_active(False)
        mentor_checked.save()

        return {"success": True, msg: "successfully logged out!"}, HTTPStatus.OK



@mentee_ns.route('/file')
class File(Resource):
    def get(self):
        # Send a file from the static folder with a MIME type of text/csv
        file = send_from_directory('static/profile/1', 'default.jpg', mimetype='image/jpg')
        # Wrap the file in a Response object from Flask-RESTX
        # return {'img': f'{file}'},200
        return mentee_ns.make_response(file, 200)
    
# @mentee_ns.route('/test')
# class Test123(Resource):
#     '''Design for testing smthg'''

#     # @mentee_ns.marshal_with(user_devices_all_model) # add schema
#     def get(self):
#         '''testx purposes'''

#         users = Users.query.all()

#         # result = []

#         # for user in users:
#         #     devices = []
#         #     for device in users.devices:
#         #         devices.append({'id': device.id, 'sn': device.serial_number, 'name': device.name})
#         #     result.append({'id': user.id, 'title': user.title, 'devices': devices})
#         # return result
    
#         res = [
#             {
#                 'id': user.id, 
#                 # 'sn': device.serial_number, 
#                 'name': user.username, 
#                 'image_url': "fix image url",
#                 'devices': [
#                     { 
#                         'id': device.id, 
#                         'sn': device.serial_number, 
#                         'name': device.name,
#                         'task': device.task
#                     } for device in user.user_devices
#                 ]
#             } for user in users
#         ]

#         return {"data": res}, HTTPStatus.OK
    

    
    

#         # ✅ Your project is ready!   
#         # To run your project, navigate to the directory and run one of the following npm commands.   
#         # - cd trackerapp                         
#         # - npm run android                     
#         # - npm run ios # you need to use macOS to build the iOS project - use the Expo app if you need to do iOS development without a Mac                                                                                    
#         # - npm run web  
        





