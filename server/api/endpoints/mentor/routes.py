
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

import jwt

from ...models.models import db, Mentors, JWTTokenBlocklist
from ...config import BaseConfig
# import requests

mentor_ns = Namespace('mentor', description='Mentor operations')

# configure a file handler for admin namespace only
mentor_ns.logger.setLevel(logging.INFO)
fh = logging.FileHandler("v3.log")
mentor_ns.logger.addHandler(fh)

# Flask-Restx schema models for api request and response data
parser = reqparse.RequestParser()

upload_parser = mentor_ns.parser()

upload_parser.add_argument('profile_picture', 
                           location='files', 
                           type = FileStorage, 
                           required=True, 
                        #    action='append'
                        )

mentor_signup_model = mentor_ns.model('MentorSignUpModel', {
                                            "fullname": fields.String(required=True, min_length=2, max_length=32),
                                            "matricule": fields.String(required=True, min_length=2, max_length=32),
                                            "username": fields.String(required=True, min_length=2, max_length=32),
                                            "email": fields.String(required=True, min_length=4, max_length=64),
                                            "password": fields.String(required=True, min_length=6, max_length=16),
                                            "department": fields.String(required=True, min_length=3, max_length=32),
                                        })

mentor_login_model = mentor_ns.model('MentorLoginModel', {
                                        "email": fields.String(required=True, min_length=4, max_length=64),
                                        "password": fields.String(required=True, min_length=4, max_length=16)
                                        })

mentor_edit_model = mentor_ns.model('MentorEditModel', {"userID": fields.String(required=True, min_length=1, max_length=32),
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



@mentor_ns.route('/v1/auth/signup')
class Register(Resource):
    """
       Creates a new mentor by taking 'mentor_sign_up_model' input
    """

    @mentor_ns.expect(mentor_signup_model, validate=True)
    def post(self):

        req_data = request.get_json()

        _username = req_data.get("username")
        _fullname = req_data.get("fullname")
        _matricule = req_data.get("matricule")
        _email = req_data.get("email")
        _password = req_data.get("password")
        _department = req_data.get("department")

        mentor_exists = Mentors.get_by_email(_email)
        if mentor_exists:
            # add log
            return {"success": False,
                    "msg": "Email already taken"}, HTTPStatus.BAD_REQUEST

        new_mentor = Mentors(
            username=_username, 
            fullnamee=_fullname,
            matricule=_matricule,
            email=_email,
            department=_department
            )

        new_mentor.set_password(_password)
        new_mentor.save()

        return {"success": True,
                "userID": new_mentor.id,
                "msg": "The user was successfully registered"}, HTTPStatus.CREATED


@mentor_ns.route('/v1/auth/signin')
class Login(Resource):
    """
       Login user by taking 'mentor_login_model' input and return JWT token
    """

    @mentor_ns.expect(mentor_login_model, validate=True)
    def post(self):

        req_data = request.get_json()

        _email = req_data.get("email")
        _password = req_data.get("password")

        mentor_exists = Mentor.get_by_email(_email)

        if not mentor_exists:
            return {"success": False,
                    "msg": "This email does not exist."}, HTTPStatus.BAD_REQUEST

        if not mentor_exists.check_password(_password):
            return {"success": False,
                    "msg": "Wrong credentials."}, HTTPStatus.BAD_REQUEST

        # create access token uwing JWT
        token = jwt.encode({'email': _email, 'exp': datetime.utcnow() + timedelta(minutes=30)}, BaseConfig.SECRET_KEY)

        mentor_exists.set_jwt_auth_active(True)
        mentor_exists.save()

        access_token = create_access_token(identity=_email, expires_delta=timedelta(minutes=45))

        image_url = url_for('static', filename=f'profile/{mentor_exists.profile_photo}', _external=True)

        return {"success": True,
                "token": access_token,
                "user": mentor_exists.toJSON(),
                "image_url": image_url
                }, HTTPStatus.CREATED


@mentor_ns.route('/v1/mentor/edit')
class EditUser(Resource):
    """
       Edits Mentor's username or password or both using 'mentor_edit_model' 
    """

    @mentor_ns.expect(mentor_edit_model)
    @jwt_required
    def patch(self):

        current_user = get_jwt_identity()
        # admin_info = Admin.query.filter_by(email=current_user).first()

        req_data = request.get_json()

        _new_username = req_data.get("username")
        _new_email = req_data.get("email")

        if _new_username:
            self.update_username(_new_username)

        if _new_email:
            self.update_email(_new_email)

        self.save()

        return {"success": True}, HTTPStatus.ACCEPTED
    

    @mentor_ns.expect(upload_parser)
    @jwt_required
    def put(self, current_user): #
        '''Upload profile picture'''

        args = upload_parser.parse_args()
        file = args['profile_picture']

        current_user = get_jwt_identity()
        mentor_updates = Admin.query.filter_by(email=current_user).first()

        # mentor_updates = Users.query.filter_by(id=int(current_user)).first() #current_user._id # replace with the technique bove
        
        if file is None:
                # add logs
                return {"success": False, "msg": "Field not found, please resend!"}, HTTPStatus.NO_CONTENT #401
        
        if mentor_updates is None:
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
            if file_ext not in current_app.config['UPLOAD_EXTENSIONS'] or file_ext != validate_image(file.stream):
                abort(400)
                # add logs
                # return{}, 400
            file.save(os.path.join(path, filename))

        mentor_updates.profile_photo = filename
        db.session.commit()

        return {"success": True,
                "msg": "Image uploaded with success" }, HTTPStatus.ACCEPTED   


@mentor_ns.route('/v1/auth/logout')
class LogoutUser(Resource):
    """
       Logs out Mentot using 'Mentor_logout_model' 
    """

    @jwt_required
    def post(self, current_user):

        # _jwt_token = request.headers["authorization"]
        _JWT_token = request.headers.get('Authorization')

        jwt_block = JWTTokenBlocklist(jwt_token=_JWT_token , created_at=datetime.now(timezone.utc))
        jwt_block.save()

        self.set_jwt_auth_active(False)
        self.save()

        current_mentor = get_jwt_identity()

        mentor_checked = Mentors.get_by_id(current_mentor)
        print(mentor_checked)
        mentor_checked.set_jwt_auth_active(False)
        mentor_checked.save()

        return {"success": True, msg: "successfully logged out!"}, HTTPStatus.OK


  