import click
import csv
from datetime import datetime

from .models import User, Topic, Room, Message
from . import db
from config import BASE_DIR

Models = {
    'User': 'base_user.csv',
    'Topic': 'base_topic.csv',
    'Room': 'base_room.csv',
    'Message': 'base_message.csv',
    'room_user_m2m': 'base_room_participants.csv',
}


@click.command('import_data')
def import_data_command():
    """Fill db with test data."""

    for model, csv_files in Models.items():
        with open(
            f'{BASE_DIR}/rooms/data/{csv_files}',
            'r',
            encoding='utf-8-sig'
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                if model == 'User':
                    item = User(
                        username=row['username'],
                        password=row['password'],
                        email=row['email'],
                        name=row['name']
                    )
                    item.about_me = row['about_me']
                    item.joined = datetime.utcnow()
                    item.id = int(row['user_id'])

                if model == 'Topic':
                    item = Topic(row['name'])
                    item.id = int(row['id'])

                if model == 'Room':
                    user = db.session.get(User, int(row['host_id']))
                    topic = db.session.get(Topic, int(row['topic_id']))
                    item = Room(
                        host=user,
                        topic=topic,
                        head=row['head'],
                        description=row['description'],
                        image_path=row['image'],
                        link=row['link']
                    )
                    item.id = int(row['id'])
                    item.created = datetime.utcnow()
                    item.updated = datetime.utcnow()

                if model == 'Message':
                    user = db.session.get(User, int(row['author_id']))
                    room = db.session.get(Room, int(row['room_id']))
                    item = Message(
                        author=user,
                        room=room,
                        body=row['body']
                    )
                    item.created = datetime.utcnow()

                if model == 'room_user_m2m':
                    user = db.session.get(User, int(row['user_id']))
                    item = db.session.get(Room, int(row['room_id']))

                    item.participants.append(user)

                db.session.add(item)
                db.session.commit()

    click.echo('All test data is added successfully.')
