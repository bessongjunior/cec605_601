

import os
from datetime import datetime, timezone, timedelta
from http import HTTPStatus
from functools import wraps
import logging, jwt

from flask import request, url_for, current_app
from flask_restx import Namespace, Resource, fields, reqparse
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from sqlalchemy import or_
# from flask_sqlalchemy import or_
from flask_jwt_extended import create_access_token, get_jwt_identity,jwt_required

from ...models.models import db, Admin, JWTTokenBlocklist
# from from backend.api.models.models import db, Admin
# from ....config import BASE_DIR, BaseConfig


admin_ns = Namespace('admin', description='Admin related operations')


# configure a file handler for admin namespace only
admin_ns.logger.setLevel(logging.INFO)
fh = logging.FileHandler("v1.log")
admin_ns.logger.addHandler(fh)

admin_reg_model = admin_ns.model('RegistrationModel', {
    "fullname": fields.String(),
    "username": fields.String(),
    "email": fields.String(), 
    "password": fields.String(),
})

admin_login_model = admin_ns.model('LoginModel', {
    "email": fields.String(),
    "password": fields.String()
})

admin_edit_model = admin_ns.model('EditModel', {
    "username": fields.String(),
    "email": fields.String()
})

create_community_model = admin_ns.model('CommunityCreate', {
    'name': fields.String(required=True, description='Name of the community'),
})


parser = reqparse.RequestParser()
upload_parser = admin_ns.parser()
upload_parser.add_argument('profile_picture', 
                           location='files', 
                           type = FileStorage, 
                           required=True, 
                        #    action='append'
                        )

allowed_extensions = set(['jpg', 'png', 'jpeg', 'gif'])

"""Helper function for JWT token required"""

def allowed_file(filename):
    '''check if the file name has our valide extension'''
    for filetype in allowed_extensions:
        return filetype
    # return filetype in allowed_extensions


''' Routes '''

# token not required

@admin_ns.route('/v1/register')
class RegisterAdmin(Resource):
    ''' Registration resource route'''

    @admin_ns.expect(admin_reg_model)
    def post(self, **kwargs):
        '''Admin registration endpoint'''

        req_data = request.get_json()

        _fullname = req_data.get('fullname')
        _username = req_data.get('username')
        _email = req_data.get('email')
        _password = req_data.get('password')


        # check if user email exist
        check_email = Admin.find_by_email(_email)
        
        if not check_email is None:
            # add logs
            return {
                "Success": False,
                "msg": "email already exits"
            }, HTTPStatus.BAD_REQUEST
        
        new_admin = Admin(fullname=_fullnamee, username=_username, email=_email)

        new_admin.set_password(_password)

        new_admin.save()

        return {"success": True,
                "userID": new_admin.id,
                "msg": "The user was successfully registered"
                }, HTTPStatus.CREATED


@admin_ns.route('/v1/login')
class LoginAdmin(Resource):
    ''' Login resource route'''

    @admin_ns.expect(admin_login_model)
    def post(self):
        '''Admin Login endpoint'''

        req_data = request.get_json()

        _email = req_data.get("email")
        _password = req_data.get("password")

        admin_exists = Admin.find_by_email(_email)

        if not admin_exists:
            admin_ns.logger.info(f"Administrator donot exist, the email '{_email}' was use, attempting to login on an admin account")
            return {"success": False,
                    "msg": "This email does not exist."}, HTTPStatus.BAD_REQUEST

        if not admin_exists.check_password(_password):
            admin_ns.logger.info(f"Administrator exist, the admin with email '{_email}' was use, password did not match")
            return {"success": False,
                    "msg": "Wrong credentials."}, HTTPStatus.UNPROCESSABLE_ENTITY 

        # create access token uwing JWT
        token = jwt.encode({'email': _email, 'exp': datetime.utcnow() + timedelta(minutes=30)}, BaseConfig.SECRET_KEY)

        access_token = create_access_token(identity=_email, expires_delta=timedelta(minutes=45))

        admin_exists.set_jwt_auth_active(True)
        admin_exists.save()

        image_url = url_for('static', filename=f'profile/admin/{admin_exists.profile}', _external=True)

        return {"success": True,
                "token": access_token,
                "users": admin_exists.toJSON(),
                # "image_url": image_url
                }, HTTPStatus.CREATED


@admin_ns.route('/v1/resetpassword')
class ResetPassword(Resource):
    '''Resource endpoint to reset password'''

    def post(self):
        '''Endpoint to reset password'''

        req_data = request.get_json()

        _email = req_data.get("email")
        _new_password = req_data.get("password")

        # check if email exist in database
        check_mail = Admin.find_by_email(_email)

        if not check_mail:
            # add logs
            return {
                "success": False,
                "msg": f"Sorry Your email: {_email} is not Found."
            }, HTTPStatus.UNPROCESSABLE_ENTITY
        
        # Hashing password before saving in database
        check_mail.set_password(_new_password)

        db.session.commit()

        return {"success": True, "msg": "Password successfully updated. Login Now."}, HTTPStatus.ACCEPTED

# Token required

@admin_ns.route('/v1/logout')
class LogoutAdmin(Resource):
    ''' Logout resource route'''

    @jwt_required
    def post(self):
        """Endpoint for admin to logout"""

        _JWT_token = request.headers.get('Authorization')
        # _jwt_token = request.headers["authorization"]
        current_user = get_jwt_identity()

        admin_check = Admin.find_by_id(current_user)
        print(admin_check)
        admin_check.set_jwt_auth_active(False)
        admin_check.save()

        return {"success": True, "msg": "successfully logged out!"}, HTTPStatus.OK


@admin_ns.route('/v1/profile-info')
class AdminUserInfo(Resource):
    '''Resource for admin Profil Details'''

    @jwt_required()
    def get(self):
        '''Endpoint which returns admin profile info'''

        current_user = get_jwt_identity()
        admin_info = Admin.query.filter_by(email=current_user).first()

        res = {
                'date_joined': f'{admin_info.date_joined}',
                'email': admin_info.email,
                'name': admin_info.admin_username,
                'image_url':  url_for('static', filename=f'profile/admin/{admin_info.profile}', _external=True),
                'username': f"{admin_info.first_name} {admin_info.last_name}",
                'location': 'Cameroon',
        }

        return res, HTTPStatus.OK


@admin_ns.route('/v1/edit')
class EditAdminDetails(Resource):
    ''' Edit resource route'''

    @admin_ns.expect(admin_edit_model)
    # @token_required
    @jwt_required()
    def patch(self):
        '''Admin endpoint to edit personal details'''

        req_data = request.get_json()
        current_user = get_jwt_identity()

        _new_username = req_data.get("username")
        _new_email = req_data.get("email")
        _contact = req_data.get("contact")

        # print(req_data)
        # print(current_user)


        admin_updates = Admin.query.filter_by(email=current_user).first()

        print(admin_updates)
        admin_updates.admin_username = _new_username
        admin_updates.email = _new_email
        # admin_updates.contact = _contact

        # if _new_username:
        #     self.update_username(_new_username)
        
        # if _new_email:
        #     self.update_email(_new_email)

        db.session.commit()

        return {"success": True, "msg": "username and email successfully updated."}, HTTPStatus.ACCEPTED

    @admin_ns.expect(upload_parser)
    # @token_required
    @jwt_required()
    def put(self, current_user):
        '''Admin profile picture upload endpoint'''

        args = upload_parser.parse_args()
        file = args['profile_picture']

        admin_updates = Admin.query.filter_by(id=int(current_user.id)).first()

        if file is None:
                # add logs
                return {"success": False, "msg": "Field not found, please resend!"}, HTTPStatus.NO_CONTENT
        
        if admin_updates is None:
                # add logs
                return{"success": False, "msg":"The param 'id' mismatch"}, HTTPStatus.BAD_REQUEST
        
        
        if not allowed_file(file.filename):
                # add logs 
                return {'success': False, 'msg': 'file type not accepted'}, HTTPStatus.FORBIDDEN
        
        if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # print(filename)
                file.save(os.path.join(current_app.config['UPLOAD_PICTURE']+"/admin", filename))


        filename = secure_filename(file.filename)
        admin_updates.profile = filename

        db.session.commit()

        return {
             "success": True,
             "msg": "Profile picture successfully uploads"
        }, HTTPStatus.ACCEPTED   




# Endpoint for the admin to create a Community
@admin_ns.route('/v1/create/community')
class AdminCreateCommunity(Resource):
    @jwt_required()  # Assuming you use JWT for authentication
    @admin_ns.expect(create_community_model, validate=True)
    def post(self):
        try:
            current_user_id = get_jwt_identity()

            # Check if the current user is an admin
            current_user = get_jwt_identity()
            is_admin = Admin.query.filter_by(email=current_user).first()



            if not is_admin:
                return {"success": False,'message': 'Only admins can create communities'}, 403

            # Assuming the request contains the community data in the JSON data
            community_data = request.get_json()

            # Create a new community
            new_community = Community(**community_data)
            db.session.add(new_community)
            db.session.commit()

            return {"success": True,'message': 'Community created successfully'}, HTTPStatus.CREATED

        except Exception as e:
            # Handle exceptions appropriately
            return {"success": False,'message': f'Error creating community: {str(e)}'}, 500


# Endpoint for the admin to update a Community
@admin_ns.route('/v1/update/community/<int:id>', methods=['PUT'])
class AdminUpdateCommunity(Resource):
    @jwt_required()
    @admin_ns.expect(create_community_model, validate=True)
    def put(self, id):
        try:
            # Check if the current user is an admin
            current_user = get_jwt_identity()
            is_admin = Admin.query.filter_by(email=current_user).first()

            if not is_admin:
                return {"success": False, 'message': 'Only admins can update communities'}, 403

            # Get the community to update
            community = Community.query.get(id)
            if not community:
                return {"success": False, 'message': 'Community not found'}, 404

            # Update the community
            community_data = request.get_json()
            for key, value in community_data.items():
                setattr(community, key, value)
            db.session.commit()

            return {"success": True, 'message': 'Community updated successfully'}, HTTPStatus.OK

        except Exception as e:
            return {"success": False, 'message': f'Error updating community: {str(e)}'}, 500

# Endpoint for the admin to delete a Community
@admin_ns.route('/v1/delete/community/<int:id>', methods=['DELETE'])
class AdminDeleteCommunity(Resource):
    @jwt_required()
    def delete(self, id):
        try:
            # Check if the current user is an admin
            current_user = get_jwt_identity()
            is_admin = Admin.query.filter_by(email=current_user).first()

            if not is_admin:
                return {"success": False, 'message': 'Only admins can delete communities'}, 403

            # Get the community to delete
            community = Community.query.get(id)
            if not community:
                return {"success": False, 'message': 'Community not found'}, 404

            # Delete the community
            db.session.delete(community)
            db.session.commit()

            return {"success": True, 'message': 'Community deleted successfully'}, HTTPStatus.OK

        except Exception as e:
            return {"success": False, 'message': f'Error deleting community: {str(e)}'}, 500

# Endpoint for the admin to list all Communities
@admin_ns.route('/v1/list/communities')
class AdminListCommunities(Resource):
    @jwt_required()
    def get(self):
        try:
            # Check if the current user is an admin
            current_user = get_jwt_identity()
            is_admin = Admin.query.filter_by(email=current_user).first()

            if not is_admin:
                return {"success": False, 'message': 'Only admins can list communities'}, 403

            # Get all communities
            communities = Community.query.all()
            communities_list = [community.name for community in communities]

            return {"success": True, 'communities': communities_list}, HTTPStatus.OK

        except Exception as e:
            return {"success": False, 'message': f'Error listing communities: {str(e)}'}, 500


# @admin_ns.route('/v1/users/<search_term>')
# class SearchUser(Resource):
#     '''Resource endpoint to Search and return user data'''

#     # @token_required
#     @jwt_required()
#     def get(self, search_term):
#         '''endpoint to Search and return user data'''

#         # results = Users.query.filter(Users.email.like('%'+search_term+'%')).all()
        
#         results = Users.query.filter(or_(Users.phone_number.like('%'+search_term+'%'), Users.email.like('%'+search_term+'%'))).first()
#         # print(results)
#         if not results:
#             return {'success': False, 'msg': f'{search_term} not found, try again!'}, 404
        
#         res = {
#                 'username': results.username,
#                 'email': results.email,
#                 'firstname': results.firstname,
#                 'lastname': results.lastname,
#                 'phone': results.phone_number,
#                 'date_joined': f'{results.date_joined}'}
#             # } for result in results
#         # print(res)

#         if results:
#             return res, 200
            


