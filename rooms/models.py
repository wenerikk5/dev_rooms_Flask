from datetime import datetime

from flask_login import UserMixin

import sqlalchemy as sa
from werkzeug.security import generate_password_hash, check_password_hash

from . import db


room_user_m2m = db.Table(
    'room_user',
    sa.Column('room_id', sa.ForeignKey('room.id'), primary_key=True),
    sa.Column('user_id', sa.ForeignKey('user.id'), primary_key=True),
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100))

    room_participants = db.relationship(
        'Room',
        secondary=room_user_m2m,
        cascade="all, delete"
    )

    def __init__(self, username, password, name):
        self.username = username
        self.password = generate_password_hash(password)
        if name:
            self.name = name

    def check_password(self, pwd: str):
        return check_password_hash(self.password, pwd)
    
    def set_password(self, password: str):
        self.password = generate_password_hash(password)

    def __repr__(self):
        return self.username   


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def rooms_count(self):
        # num_of_rooms = Topic.query.join(Room).filter(self.id == Room.topic_id).count()
        num_of_rooms = Room.query.filter(Room.topic_id == self.id).count()
        return num_of_rooms

    def __repr__(self):
        return self.name
    

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text())
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))

    author = db.relationship('User', backref=db.backref('message', lazy='dynamic'))
    
    def __repr__(self):
        return self.body[0:30]


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    head = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text())
    link = db.Column(db.String(255))
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    host_id = db.Column(db.Integer, db.ForeignKey('user.id'))  
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    image_path = db.Column(db.String(255))

    host = db.relationship('User', backref=db.backref('room', lazy='dynamic'))
    topic = db.relationship('Topic', backref=db.backref('room', lazy='dynamic'))
    messages = db.relationship('Message', backref=db.backref('room'), cascade="all, delete")
    participants = db.relationship(
        'User',
        secondary=room_user_m2m,
        overlaps="room_participants"
    )

    def get_topic_name(self):
        return self.topic.name

    def __repr__(self):
        return f'Room {self.head}'
    
