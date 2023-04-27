import pytest
from rooms import create_app, db
from rooms.models import User, Topic, Room, Message


@pytest.fixture()
def app():
    app = create_app('config.TestingConfig')

    with app.app_context():
        db.create_all()

        yield app

        db.drop_all()   


@pytest.fixture()
def client(app):
    with app.app_context():
        yield app.test_client()


@pytest.fixture()
def runner(app):    
    yield app.test_cli_runner()


@pytest.fixture()
def init_database(client):
    # Create db and all tables
    db.create_all()

    # Insert user data
    user1 = User('user1', '123', 'User1')
    user2 = User('user2', '123', 'User2')
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

    yield

    db.drop_all()


@pytest.fixture()
def init_database_main(init_database):

    user1 = db.session.get(User, 1)
    user2 = db.session.get(User, 2)

    room1 = Room(
        host=user1,
        topic=Topic('Python'),
        head='Test Python',
        description='About Python',
        link='#Python'
    )
    room2 = Room(
        host=user2,
        topic=Topic('Rust'),
        head='Test Rust',
        description='About Rust',
        link='#Rust'
    )

    db.session.add(room1)
    db.session.add(room2)
    db.session.commit()

    yield


@pytest.fixture()
def login_default_user(client):
    client.post('/login',
                data=dict(username='user1', password='123', name='User1'),
                follow_redirects=True)

    yield

    client.get('/logout', follow_redirects=True)


@pytest.fixture()
def new_user():
    user = User('testuser', 'TestPassword', 'TestUser')
    return user

