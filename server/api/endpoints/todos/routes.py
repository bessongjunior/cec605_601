from datetime import datetime, timezone, timedelta
import logging, os

from flask import request, url_for, current_app, abort, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource, fields, reqparse

from ...models.models import ChatConnection, Mentees, Mentors, Community, CommunityMember, Message, User
from ...config import BaseConfig


todos_ns = Namespace('task', description='Task related operations')

# configure a file handler for admin namespace only
todos_ns.logger.setLevel(logging.INFO)
fh = logging.FileHandler("v6.log")
todos_ns.logger.addHandler(fh)

create_task = todos_ns.model('CreateTask', {
    'content': fields.String,
})

update_task = todos_ns.model('UpdateTask', {
    'content': fields.String(description='Task content'),
    'status': fields.String(description='Task status'),
})



@todos_ns.route('/')
class TaskList(Resource):
    '''Get task list'''

    @jwt_required()
    def get(self):
        tasks = Task.query.all()
        return [{'id': task.id, 'content': task.content, 'status': task.status} for task in tasks]

@todos_ns.route('/')
class CreateTask(Resource):
    '''Create task endpoint'''

    @todos_ns.expect(create_task)
    @jwt_required()
    def post(self):
        data = request.get_json()
        current_mentee = Mentees.query.filter_by(email=get_jwt_identity()).first()
        new_task = Task(content=data['content'], status=data['status'], mentees_id=current_mentee.id)
        db.session.add(new_task)
        db.session.commit()
        return {'id': new_task.id, 'success': True, 'message': 'Task create with succes'}, HTTPStatus.CREATED

@todos_ns.route('/update/<int:id>')
class UpdateTask(Resource):
    '''update task status and/content''' 

    @todos_ns.expect(update_task)
    @jwt_required()
    def put(self, id):
        task = Task.query.get_or_404(id)
        data = request.get_json()
        if task.owner.email != get_jwt_identity():
            return {'message': 'You can only update your own tasks'}, 403
        task.content = data.get('content', task.content)
        task.status = data.get('status', task.status)
        db.session.commit()
        return {'id': task.id,  'success': True, 'message': 'Task update with succes'}, HTTPStatus.CREATED

@todos_ns.route('/delete/<int:id>')
class UpdateTask(Resource):
    '''Delete task'''

    @jwt_required()
    def delete(self, id):
        task = Task.query.get_or_404(id)
        db.session.delete(task)
        db.session.commit()
        return {'message': "Deleted with success!"}, 204




