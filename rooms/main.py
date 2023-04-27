import os
import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, \
    current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from . import db, ALLOWED_IMAGE_EXTENSIONS
from .models import Topic, Room, User, Message
from .forms import RoomForm

main = Blueprint('main', __name__)


def allowed_file(filename):
    return '.' in filename and filename.lower().rsplit('.', 1)[1] in ALLOWED_IMAGE_EXTENSIONS


@main.route('/')
def index():
    topics = Topic.query.order_by(Topic.name).all()

    q = request.args.get('q') if request.args.get('q') is not None else ''

    rooms = Room.query.order_by(Room.updated.desc()).all()

    if q:
        topics_filtered = Topic.query.filter(Topic.name.like('%' + q + '%')).all()
        
        if len(topics_filtered) > 0:
            rooms = Room.query.filter(Room.topic == topics_filtered[0]) \
                    .order_by(Room.updated.desc()) \
                    .all()
        else:
            rooms = Room.query \
                .filter(
                    Room.head.like('%' + q + '%') |
                    Room.description.like('%' + q + '%')
                ) \
                .order_by(Room.updated.desc()) \
                .all()

    rooms_available = len(rooms)
    rooms_total = Room.query.count()
    room_messages = Message.query.order_by(Message.created.desc()).all()

    context = {
        'topics': topics,
        'rooms': rooms,
        'rooms_available': rooms_available,
        'rooms_total': rooms_total,
        'room_messages': room_messages,
    }
    return render_template('main/index.html', **context)


@main.route('/profile/<int:id>')
def profile(id):
    user = db.session.get(User, id)
    # rooms = Room.query.filter(user.id.in_(Room.participants)).all()
    topics = Topic.query.order_by(Topic.name).all()
    room_messages = Message.query.filter(Message.author == user).order_by(Message.created.desc()).all()
    rooms_total = db.session.query(Room).count()
    
    context = {
        'user': user,
        'topics': topics,
        'rooms': user.room_participants[::-1],
        'rooms_total': rooms_total,
        'room_messages': room_messages,
    }
    return render_template('main/profile.html', **context)


@main.route('/<int:id>', methods=['GET', 'POST'])
def room_detail(id):
    room = db.session.get(Room, id)

    if not room:
        abort(404, "Room do not exist.")

    room_messages = Message.query.filter(Message.room == room).order_by(Message.created.desc())

    if request.method == 'POST':
        if current_user.is_authenticated:
            body = request.form.get('body')
            error = None

            if not body:
                error = 'Message text is required.'
            
            if error is not None:
                flash(error, 'danger')
            else:
                message = Message(
                    author=current_user,
                    body=body,
                    room=room,
                )
                room.participants.append(current_user)
                db.session.add(message)
                db.session.commit()
                # flash('Message is added.', 'success')
                return redirect(url_for('main.room_detail', id=room.id))
        return redirect(url_for('auth.login'))    

    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': room.participants,
    }
    return render_template('main/room.html', **context)


@main.route('/room-create', methods=('GET', 'POST'))
@login_required
def room_create():
    form = RoomForm()

    topics = Topic.query.all()

    if form.validate_on_submit():
        head = form.head.data
        description = form.description.data
        topic_name = request.form.get('topic')
        link = form.link.data
        image = form.image.data
        
        topic = Topic.query.filter(Topic.name == topic_name).first()

        # Create topic if it's not exist yet.
        if not topic:
            topic = Topic(topic_name)
            db.session.add(topic)
            db.session.commit()

        filename = ''
        if image:
            filename = secure_filename(image.filename)
            if allowed_file(image.filename):
                image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            else:
                flash('Not supported image extension.', 'danger')
                return render_template('main/create_room.html', form=form, topics=topics)

        existing_room = Room.query.filter(Room.head == head, Room.topic == topic).first()

        if existing_room:
            flash('Room with such head and topic is already exists.', 'danger')
            return render_template('main/create_room.html', form=form, topics=topics)
        else:
            room = Room(
                head=head,
                description=description,
                topic=topic,
                host=current_user,
                link=link,
                image_path=filename
            )
            room.participants.append(current_user)
            db.session.add(room)
            db.session.commit()
            return redirect(url_for('main.index'))
    
    if form.errors:
        flash(form.errors, 'danger')

    return render_template('main/create_room.html', form=form, topics=topics)


@main.route('/<int:id>/room-edit', methods=('GET', 'POST'))
@login_required
def room_edit(id):
    room = db.session.get(Room, id)
    form = RoomForm(obj=room)
    topics = db.session.query(Topic).all()

    if not room:
        flash("Room doesn't esixt.", 'danger')
        return redirect(url_for('main.index'))
    elif current_user != room.host:
        flash('You are not allowed to modify this room.', 'danger')
        return redirect(url_for('main.index'))
    
    if form.validate_on_submit():
        head = form.head.data
        description = form.description.data
        topic_name = request.form.get('topic')
        link = form.link.data
        image = form.image.data
        error = False

        topic = Topic.query.filter(Topic.name == topic_name).first()

        if not topic:
            topic = Topic(topic_name)
            db.session.add(topic)
            db.session.commit()
        
        filename = room.image_path

        if image:
            filename = secure_filename(image.filename)
            if allowed_file(image.filename):
                image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            else:
                flash('Not supported image extension.', 'danger')
                return render_template('main/create_room.html', room=room, form=form, topics=topics)
        
        room.head = head or room.head
        room.description = description or room.description
        room.topic = topic or room.topic
        room.link = link or room.link
        room.image_path = filename
        room.updated = datetime.datetime.utcnow()

        existing_rooms = Room.query.filter(Room.head == head, Room.topic == topic).all()

        if len(existing_rooms) > 1:
            flash('There is other existing room with such head and topic.', 'danger')
            return render_template('main/create_room.html', room=room, form=form, topics=topics)         
        else:
            db.session.add(room)
            db.session.commit()
            flash('Room is updated.', 'success')
            return redirect(url_for('main.index'))
    
    if form.errors:
        flash(form.errors, 'danger')

    return render_template('main/create_room.html', room=room, form=form, topics=topics)


@main.route('/<int:id>/room-delete', methods=('GET', 'POST'))
@login_required
def room_delete(id):
    room = db.session.get(Room, id)
    error = None

    if not room:
        error = "Room do not exist."
    elif current_user != room.host:
        error = 'You are not allowed to delete this room.'
    
    if error:
        flash(error, 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        db.session.delete(room)
        db.session.commit()
        flash('Room is deleted.', 'success')
        return redirect(url_for('main.index'))

    return render_template('main/delete.html', obj=room.head)


@main.route('/message-delete/<int:id>', methods=('GET', 'POST',))
@login_required
def message_delete(id):
    message = db.session.get(Message, id)
    error = None

    if not message:
        error = "Message do not exist."
    elif current_user != message.author:
        error = 'You are not allowed to delete this message.'
    
    if error:
        flash(error, 'danger')
        return redirect(url_for('main.room_detail', id=message.room.id))
    
    if request.method == 'POST':
        room_id = message.room.id
        db.session.delete(message)
        db.session.commit()
        flash('Message is deleted.', 'success')
        return redirect(url_for('main.room_detail', id=room_id))

    obj = message.body[:20] + '...' if len(message.body) > 20 else message.body
    return render_template('main/delete.html', obj=obj)
