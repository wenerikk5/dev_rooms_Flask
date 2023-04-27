"""
Functional tests for main blueprint.
"""
from rooms import db
from rooms.models import User, Topic, Room, Message


def test_index_page_has_room(client, init_database_main):
    """
    GIVEN an app configured for testing
    WHEN the '/' page is requested (GET)
    THEN check the response is valid
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'BROWSE TOPICS' in response.data
    assert db.session.get(Room, 1).head == 'Test Python'
    assert b'Python' in response.data
    assert b'Test Python' in response.data


def test_room_page(client, init_database_main):
    """
    GIVEN an app configured for testing
    WHEN the '/1' page is requested (GET)
    THEN check the response is valid
    """
    response = client.get('/1')
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Python' in response.data
    assert b'Test Python' in response.data

def test_incorrect_room_page(client, init_database_main):
    """
    GIVEN an app configured for testing
    WHEN the '/10' page is requested (GET)
    THEN check the response is valid
    """
    response = client.get('/10')
    assert response.status_code == 404
    assert b"Requested page do not exist yet. Please check correctness of URL." in response.data

def test_redirect_for_unathorized_room_creation(client):
    """
    GIVEN an app configured for testing
    WHEN the '/room-create' page is requested (GET)
    THEN check the redirect to Login page
    """
    response = client.get('/room-create', follow_redirects=True)
    assert response.status_code == 200
    assert b'Username' in response.data
    assert b'Create an account' in response.data

    """
    GIVEN an app configured for testing
    WHEN the '/room-create' page is requested (POST)
    THEN check the redirect to Login page
    """
    response = client.post(
        '/room-create',
        data=dict(topic='JS', head='Test JS', description='Test descritpion'),
        follow_redirects=True)
    assert response.status_code == 200
    assert b'Username' in response.data
    assert b'Create an account' in response.data

def test_valid_room_creation(client, init_database_main, login_default_user):
    """
    GIVEN an app configured for testing. User is logged in 
    WHEN the '/room-create' page is requested (POST)
    THEN check the room is created and redict to index page
    """
    response = client.post(
        '/room-create',
        data=dict(topic='JS', head='Test JS', description='Test descritpion'),
        follow_redirects=True)
    assert response.status_code == 200
    assert b'Logout' in response.data
    assert b'BROWSE TOPICS' in response.data
    assert db.session.query(Room).count() == 3
    assert db.session.get(Room, 3).head == 'Test JS'
    assert b'Test Python' in response.data
    assert b'Test JS' in response.data

def test_incorrect_room_creation(client, init_database_main, login_default_user):
    """
    GIVEN an app configured for testing. User is logged in 
    WHEN the '/room-create' page is requested (POST)
    THEN check the room is not created without head field
    """
    response = client.post(
        '/room-create',
        data=dict(topic='JS', head='', description='Test descritpion'),
        follow_redirects=True)
    assert response.status_code == 200
    assert b'Logout' in response.data
    assert b'BROWSE TOPICS' not in response.data
    assert db.session.query(Room).count() == 2
    assert b'Head' in response.data

def test_valid_room_update(client, init_database_main, login_default_user):
    """
    GIVEN an app configured for testing. User is logged in 
    WHEN the '/1/room-edit' page is requested (POST)
    THEN check the room is updated and redict to index page
    """
    assert db.session.query(Room).count() == 2
    assert db.session.get(Room, 1).host == db.session.get(User, 1)

    response = client.post(
        '/1/room-edit',
        data=dict(topic='Python', head='Test Python --updated', description=''),
        follow_redirects=True)
    assert response.status_code == 200
    assert b'Room is updated.' in response.data
    assert b'BROWSE TOPICS' in response.data
    assert db.session.query(Room).count() == 2
    assert db.session.get(Room, 1).head == 'Test Python --updated'
    assert b'Test Python --updated' in response.data

def test_incorrect_room_update(client, init_database_main, login_default_user):
    """
    GIVEN an app configured for testing. User is logged in 
    WHEN the '/2/room-edit' page is requested (POST)
    THEN check the redirect to main page without change of Room's data
    """
    assert db.session.query(Room).count() == 2
    assert db.session.get(Room, 2).host != db.session.get(User, 1)

    response = client.post(
        '/2/room-edit',
        data=dict(topic='Rust', head='Test Rust --updated', description=''),
        follow_redirects=True)
    assert response.status_code == 200
    assert b'You are not allowed to modify this room.' in response.data
    assert b'BROWSE TOPICS' in response.data
    assert db.session.query(Room).count() == 2
    assert db.session.get(Room, 2).head == 'Test Rust'

def test_valid_room_delete(client, init_database_main, login_default_user):
    """
    GIVEN an app configured for testing. User is logged in 
    WHEN the '/1/room-delete' is requested (POST)
    THEN check the room is deleted by it's host and redirect to main page
    """
    assert db.session.query(Room).count() == 2
    assert db.session.get(Room, 1).host == db.session.get(User, 1)

    response = client.post(
        '/1/room-delete',
        follow_redirects=True)
    assert response.status_code == 200
    assert b'Room is deleted.' in response.data
    assert b'BROWSE TOPICS' in response.data
    assert db.session.query(Room).count() == 1
    assert b'Test Python' not in response.data
    assert b'Test Rust' in response.data

def test_incorrect_room_delete(client, init_database_main, login_default_user):
    """
    GIVEN an app configured for testing. User is logged in 
    WHEN the '/2/room-delete' is requested (POST)
    THEN check the room is not deleted by another user and redirected to main page
    """
    assert db.session.query(Room).count() == 2
    assert db.session.get(Room, 2).host != db.session.get(User, 1)

    response = client.post(
        '/2/room-delete',
        follow_redirects=True)
    assert response.status_code == 200
    assert b'You are not allowed to delete this room.' in response.data
    assert b'BROWSE TOPICS' in response.data
    assert db.session.query(Room).count() == 2
    assert b'Test Python' in response.data
    assert b'Test Rust' in response.data

def test_room_participants(client, init_database_main, login_default_user):
    """
    GIVEN an app configured for testing. User is logged in 
    WHEN the '/3' page is requested (GET)
    THEN check the room includes author in participants
    """
    author = db.session.get(User, 1)
    response = client.post(
        '/room-create',
        data=dict(topic='JS', head='Test JS', description='Test descritpion'),
        follow_redirects=True)
    
    response = client.get('/3')
    
    assert response.status_code == 200
    assert author in db.session.get(Room, 3).participants
    assert b'Logout' in response.data
    assert b'PARTICIPANTS' in response.data
    assert b'@User1' in response.data

def test_add_message_and_participants(client, init_database_main, login_default_user):
    """
    GIVEN an app configured for testing. User is logged in 
    WHEN the '/2' Room 2 page is requested (POST)
    THEN check the messages is added and author in participants
    """
    author = db.session.get(User, 1)
    room = db.session.get(Room, 2)
    assert len(room.participants) == 0
    assert room.host.name == "User2"
    assert db.session.query(Message).count() == 0

    response = client.post(
        '/2',
        data=dict(author=author, room=room, body='Message body'),
        follow_redirects=True)
    
    response = client.get('/2')
    
    assert response.status_code == 200
    assert db.session.query(Message).count() == 1
    assert b'PARTICIPANTS' in response.data
    assert len(room.participants) == 1
    assert b'Message body' in response.data
    assert author in db.session.get(Room, 2).participants
    assert b'@User1' in response.data

    """
    THEN user's profile includes all participated rooms
    """
    response = client.get('/profile/1')

    assert response.status_code == 200
    assert b'PARTICIPATED ROOMS' in response.data
    assert b'Test Rust' in response.data

def test_add_message_by_unathorized_user(client, init_database_main):
    """
    GIVEN an app configured for testing. User is not authorized
    WHEN the '/2' Room 2 page is requested (POST)
    THEN check the redirect to Login page
    """
    room = db.session.get(Room, 2)
    assert db.session.query(Message).count() == 0

    response = client.post(
        '/2',
        data=dict(room=room, body='Message body'),
        follow_redirects=True)
    
    assert response.status_code == 200
    assert db.session.query(Message).count() == 0
    assert response.status_code == 200
    assert b'Username' in response.data
    assert b'Create an account' in response.data

def test_valid_message_delete(client, init_database_main, login_default_user):
    """
    GIVEN an app configured for testing. User is logged in 
    WHEN the '/message-delete/1' is requested (POST)
    THEN check the message is deleted and redirected to room's page
    """
    author = db.session.get(User, 1)
    room = db.session.get(Room, 2)
    assert room.host.name == "User2"
    assert db.session.query(Message).count() == 0

    response = client.post(
        '/2',
        data=dict(author=author, room=room, body='Message body'),
        follow_redirects=True)
    
    response = client.get('/2')
    
    assert response.status_code == 200
    assert db.session.query(Message).count() == 1
    assert b'PARTICIPANTS' in response.data
    assert b'Message body' in response.data
    assert b'@User1' in response.data

    response = client.post(
        '/message-delete/1',
        follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Message is deleted.' in response.data
    assert db.session.query(Message).count() == 0
    assert b'PARTICIPANTS' in response.data
    assert b'Message body' not in response.data
    assert b'@User1' in response.data
    