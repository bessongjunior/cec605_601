
from datetime import datetime, date
from typing import Optional, ClassVar


from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped
from sqlalchemy import Text, TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship, polymorphic_union
# from sqlalchemy.orm import relationship

db = SQLAlchemy()


# community
class Community(db.Model):
    __tablename__ = 'community'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    members = db.relationship('CommunityMember', back_populates='community')

class CommunityMember(db.Model):
    __tablename__ = 'community_member'
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentors.id'))
    mentee_id = db.Column(db.Integer, db.ForeignKey('mentees.id'))
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'))
    mentor = db.relationship('Mentors', back_populates='communities', foreign_keys=[mentor_id])
    mentee = db.relationship('Mentees', back_populates='communities', foreign_keys=[mentee_id])
    community = db.relationship('Community', back_populates='members')

# Mentors.communities = db.relationship('CommunityMember', back_populates='mentors', foreign_keys=[CommunityMember.mentor_id])
# mentees.communities = db.relationship('CommunityMember', back_populates='mentees', foreign_keys=[CommunityMember.mentee_id])



class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    role = db.Column(db.String(10), nullable=False)
    __mapper_args__ = {
        'polymorphic_on': role,
        'polymorphic_identity': 'user'
    }

class Mentees(User):
    id: Optional[int | str] = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True) #db.Column(db.Integer(), primary_key=True, unique=True)
    fullname: str = db.Column(db.String(), nullable=False)
    matricule: str = db.Column(db.String(), nullable=False)
    username: Mapped[str]= db.Column(db.String(), nullable=False)
    email: str = db.Column(db.String(), nullable=True, unique=True)
    password: str = db.Column(db.Text(), nullable=True)
    department: str = db.Column(db.String(), nullable=False)
    profile: str = db.Column(db.String(), nullable=False, default='default.jpg')
    jwt_auth_active: bool = db.Column(db.Boolean())
    date_joined: datetime = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, server_default=text('CURRENT_TIMESTAMP'))
    date_updated: datetime = db.Column(db.DateTime(timezone=True), onupdate=datetime.utcnow, server_default=text('CURRENT_TIMESTAMP'))
    ### id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    connections1 = db.relationship('ChatConnection', back_populates='mentee1', foreign_keys='ChatConnection.mentee1_id')
    connections2 = db.relationship('ChatConnection', back_populates='mentee2', foreign_keys='ChatConnection.mentee2_id')
    communities1 = db.relationship('CommunityMember', back_populates='mentors', foreign_keys=[CommunityMember.mentor_id])
    communities2 = db.relationship('CommunityMember', back_populates='mentees', foreign_keys=[CommunityMember.mentee_id])
    sent_messages = db.relationship('Message', back_populates='sender', foreign_keys='Message.sender_id')
    tasks = db.relationship('Task', backref='owner', lazy='dynamic')


    def __repr__(self):
        return f"User {self.username}"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def update_email(self, new_email):
        self.email = new_email

    def update_username(self, new_username):
        self.username = new_username

    def check_jwt_auth_active(self):
        return self.jwt_auth_active

    def set_jwt_auth_active(self, set_status):
        self.jwt_auth_active = set_status

    # @declared_attr
    # def username(cls):
    #     return db.column_property(
    #         db.select([User.username]).
    #         where(User.id==cls.id).
    #         as_scalar()
    #     )

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    def toDICT(self):

        cls_dict = {}
        cls_dict['_id'] = self.id
        cls_dict['username'] = self.username
        cls_dict['email'] = self.email

        return cls_dict

    def toJSON(self):

        return self.toDICT()

Mentees.communities = db.relationship('CommunityMember', back_populates='mentees', foreign_keys=[CommunityMember.mentee_id])


class JWTTokenBlocklist(db.Model):
    id: int = db.Column(db.Integer(), primary_key=True)
    jwt_token: str = db.Column(db.String(), nullable=False)
    created_at: datetime = db.Column(db.DateTime(), nullable=False)

    def __repr__(self):
        return f"Expired Token: {self.jwt_token}"

    def save(self):
        db.session.add(self)
        db.session.commit()


class Admin(db.Model):
    '''This represent our admin table in db'''

    id: int = db.Column(db.Integer, primary_key=True)
    fullname: str = db.Column(db.String, nullable=False)
    last_name: str = db.Column(db.String, nullable=False)
    username: str = db.Column(db.String, nullable=False, unique=True)
    email: str = db.Column(db.String, nullable=False, unique=True)
    password: str = db.Column(db.String, nullable=True, unique=False)
    jwt_auth_active = db.Column(db.Boolean())
    date_joined: datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_modified: datetime = db.Column(db.DateTime, onupdate=datetime.utcnow)
    profile: str = db.Column(db.String, unique=False, nullable=False, default='profile.jpg')


    def __repr__(self):
        return f"Admin {self.admin_username}"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def check_jwt_auth_active(self):
        return self.jwt_auth_active

    def set_jwt_auth_active(self, set_status):
        self.jwt_auth_active = set_status

    def update_email(self, new_email):
        self.email = new_email

    def update_username(self, new_username):
        self.admin_username = new_username

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    def toDICT(self):

        cls_dict = {}
        cls_dict['_id'] = self.id
        cls_dict['username'] = self.admin_username
        cls_dict['email'] = self.email

        return cls_dict

    def toJSON(self):

        return self.toDICT()


# chatconnection
class ChatConnection(db.Model):
    __tablename__ = 'mentee_mentor_chat_connection'
    id = db.Column(db.Integer, primary_key=True)
    mentee1_id = db.Column(db.Integer, db.ForeignKey('mentees.id'))
    mentee2_id = db.Column(db.Integer, db.ForeignKey('mentees.id'))
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentors.id'))
    mentee1 = db.relationship('Mentees', back_populates='connections1', foreign_keys=[mentee1_id])
    mentee2 = db.relationship('Mentees', back_populates='connections2', foreign_keys=[mentee2_id])
    mentor = db.relationship('Mentors', back_populates='mentor_connections', foreign_keys=[mentor_id])

Mentees.connections1 = db.relationship('ChatConnection', back_populates='mentee1', foreign_keys=[ChatConnection.mentee1_id])
Mentees.connections2 = db.relationship('ChatConnection', back_populates='mentee2', foreign_keys=[ChatConnection.mentee2_id])


class Mentors(db.Model):
    id: Optional[int | str] = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    fullname: str = db.Column(db.String(), nullable=False)
    matricule: str = db.Column(db.String(), nullable=False)
    username: str = db.Column(db.String(), nullable=False)
    email: str = db.Column(db.String(), nullable=True, unique=True)
    password: str = db.Column(db.Text(), nullable=True)
    department: str = db.Column(db.String(), nullable=False)
    profile: str = db.Column(db.String(), nullable=False, default='default.jpg')
    jwt_auth_active: bool = db.Column(db.Boolean())
    date_joined: datetime = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, server_default=text('CURRENT_TIMESTAMP'))
    date_updated: datetime = db.Column(db.DateTime(timezone=True), onupdate=datetime.utcnow, server_default=text('CURRENT_TIMESTAMP'))
    mmentor_connections = db.relationship('ChatConnection', back_populates='mentor', foreign_keys='ChatConnection.mentor_id')
    communities = db.relationship('CommunityMember', back_populates='mentors', foreign_keys=[CommunityMember.mentor_id])
    sent_messages = db.relationship('Message', back_populates='sender', foreign_keys='Message.sender_id')

    __mapper_args__ = {
        'polymorphic_identity': 'mentor'
    }

    def __repr__(self):
        return f"User {self.username}"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def update_email(self, new_email):
        self.email = new_email

    def update_username(self, new_username):
        self.username = new_username

    def check_jwt_auth_active(self):
        return self.jwt_auth_active

    def set_jwt_auth_active(self, set_status):
        self.jwt_auth_active = set_status

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    def toDICT(self):

        cls_dict = {}
        cls_dict['_id'] = self.id
        cls_dict['username'] = self.username
        cls_dict['email'] = self.email

        return cls_dict

    def toJSON(self):

        return self.toDICT()

Mentors.communities = db.relationship('CommunityMember', back_populates='mentors', foreign_keys=[CommunityMember.mentor_id])
Mentors.mentor_connections = db.relationship('ChatConnection', back_populates='mentors', foreign_keys=[ChatConnection.mentor_id])

# chatconnections
# class MenteeMentorChatConnection(db.Model):
#     __tablename__ = 'mentee_mentor_chat_connection'
#     id = db.Column(db.Integer, primary_key=True)
#     mentee_id = db.Column(db.Integer, db.ForeignKey('mentees.id'))
#     mentor_id = db.Column(db.Integer, db.ForeignKey('mentors.id'))
#     mentee = db.relationship('Mentees', back_populates='mentor_connections', foreign_keys=[mentee_id])
#     mentor = db.relationship('Mentors', back_populates='mentee_connections', foreign_keys=[mentor_id])

# Mentees.mentor_connections = db.relationship('MenteeMentorChatConnection', back_populates='mentee', foreign_keys=[MenteeMentorChatConnection.mentee_id])
# Mentors.mentee_connections = db.relationship('MenteeMentorChatConnection', back_populates='mentor', foreign_keys=[MenteeMentorChatConnection.mentor_id])

# class MenteeMenteeChatConnection(db.Model):
#     __tablename__ = 'mentee_mentee_chat_connection'
#     id = db.Column(db.Integer, primary_key=True)
#     mentee1_id = db.Column(db.Integer, db.ForeignKey('mentees.id'))
#     mentee2_id = db.Column(db.Integer, db.ForeignKey('mentees.id'))
#     mentee1 = db.relationship('Mentees', back_populates='mentee_connections1', foreign_keys=[mentee1_id])
#     mentee2 = db.relationship('Mentees', back_populates='mentee_connections2', foreign_keys=[mentee2_id])

# Mentees.mentee_connections1 = db.relationship('MenteeMenteeChatConnection', back_populates='mentee1', foreign_keys=[MenteeMenteeChatConnection.mentee1_id])
# Mentees.mentee_connections2 = db.relationship('MenteeMenteeChatConnection', back_populates='mentee2', foreign_keys=[MenteeMenteeChatConnection.mentee2_id])


# # community
# class Community(db.Model):
#     __tablename__ = 'community'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255), nullable=False)
#     # Add other community-specific fields
#     members = db.relationship('CommunityMember', back_populates='community')

# class CommunityMember(db.Model):
#     __tablename__ = 'community_member'
#     id = db.Column(db.Integer, primary_key=True)
#     mentor_id = db.Column(db.Integer, db.ForeignKey('mentors.id'))
#     mentee_id = db.Column(db.Integer, db.ForeignKey('mentees.id'))
#     community_id = db.Column(db.Integer, db.ForeignKey('community.id'))
#     mentor = db.relationship('Mentors', back_populates='communities', foreign_keys=[mentor_id])
#     mentee = db.relationship('Mentees', back_populates='communities', foreign_keys=[mentee_id])
#     community = db.relationship('Community', back_populates='members')

# Mentors.communities = db.relationship('CommunityMember', back_populates='mentors', foreign_keys=[CommunityMember.mentor_id])
# Mentees.communities = db.relationship('CommunityMember', back_populates='mentees', foreign_keys=[CommunityMember.mentee_id])


# # messages 

# class Message(Base):
#     __tablename__ = 'message'
#     id = Column(Integer, primary_key=True)
#     sender_id = Column(Integer)
#     community_id = Column(Integer, ForeignKey('community.id'))
#     content = Column(Text, nullable=False)
#     timestamp = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP')
#     mentor = relationship('Mentor', back_populates='sent_messages', foreign_keys=[sender_id])
#     mentee = relationship('Mentee', back_populates='sent_messages', foreign_keys=[sender_id])
#     community = relationship('Community', back_populates='messages')

# Mentor.sent_messages = relationship('Message', back_populates='mentor', foreign_keys=[Message.sender_id])
# Mentee.sent_messages = relationship('Message', back_populates='mentee', foreign_keys=[Message.sender_id])
# Community.messages = relationship('Message', back_populates='community')


# messages
class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer)
    sender_role = db.Column(db.String(10))
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'))
    content = db.Column(Text, nullable=False)
    timestamp = db.Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    sender = db.relationship('User', back_populates='sent_messages', foreign_keys=[sender_id])

Community.messages = db.relationship('Message', back_populates='community')


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(128))
    status = db.Column(db.String(32))
    mentees_id = db.Column(db.Integer, db.ForeignKey('mentees.id'))

