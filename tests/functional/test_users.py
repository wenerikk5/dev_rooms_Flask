"""
Functional tests for auth blueprint.
"""
from rooms import db
from rooms.models import User


def test_login_page(client):
    """
    GIVEN an app configured for testing
    WHEN the '/login' page is requested (GET)
    THEN check the response is valid
    """
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Username' in response.data
    assert b'Password' in response.data


def test_valid_login_logout(client, init_database):
    """
    GIVEN an app configured for testing
    WHEN the '/login' page is posted (POST)
    THEN check the response is valid
    """
    response = client.post('/login',
                    data=dict(username='user1', password='123', name='User1'),
                    follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome, User1' in response.data
    assert b'Logout' in response.data
    assert b'Login' not in response.data
    """
    GIVEN an app configured for testing
    WHEN the '/logout' page is requested (GET)
    THEN check the response is valid
    """
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have successfully logged out.' in response.data
    assert b'Login' in response.data


def test_incorrect_login(client, init_database):
    """
    GIVEN an app configured for testing
    WHEN the '/login' page is posted wtih incorrect credentials (POST)
    THEN check an error message is returned
    """
    response = client.post('/login',
                    data=dict(username='user2', password='1234'),
                    follow_redirects=True)
    assert response.status_code == 200
    assert b'Incorrect credentials.' in response.data
    assert b'Logout' not in response.data
    assert b'Login' in response.data
    assert b'Username' in response.data


def test_client_already_logged_in(client, init_database, login_default_user):
    """
    GIVEN an app configured for testing
    WHEN the '/login' page is posted (POST) when the user is already logged in
    THEN check an error message is returned
    """
    response = client.post('/login',
                    data=dict(username='user1', password='123'),
                    follow_redirects=True)
    assert response.status_code == 200
    assert b'You are already logged in.' in response.data
    assert b'Logout' in response.data
    assert b'TOPICS' in response.data


def test_valid_registration(client, init_database):
    """
    GIVEN an app configured for testing
    WHEN the '/register' page is posted (POST)
    THEN check the reponse is valid and redirected to login page
    """
    response = client.post('/register',
        data=dict(username='user3', password='345', confirm='345', name='User3'),
        follow_redirects=True)
    assert response.status_code == 200
    assert db.session.query(User).count() == 3
    assert b'You are now registered.' in response.data
    assert b'Create an account' in response.data
    assert b'Logout' not in response.data
    """
    GIVEN an app configured for testing
    WHEN the '/login' page is posted (POST) with newly registered data
    THEN check the reponse is valid and redirected to profile page
    """
    response = client.post('/login',
        data=dict(username='user3', password='345'),
        follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome, User3' in response.data
    assert b'Logout' in response.data
    assert b'ABOUT' in response.data


def test_incorrect_registration(client, init_database):
    """
    GIVEN an app configured for testing
    WHEN the '/register' page is posted with incorrect credentials (POST)
    THEN check an error message is returned
    """
    response = client.post('/register',
        data=dict(username='user3', password='345', confirm='3456', name='User3'),
        follow_redirects=True)
    assert response.status_code == 200
    assert db.session.query(User).count() == 2
    assert b'You are now registered.' not in response.data
    assert b'Create an account' not in response.data
    assert b'Login' in response.data
    assert b'Username' in response.data


def test_duplicate_registration(client, init_database):
    """
    GIVEN an app configured for testing
    WHEN the '/register' page is posted (POST) using an username already registered
    THEN check an error message is returned
    """
    # Register the new account
    client.post('/register',
        data=dict(username='user3', password='345', confirm='345', name='User3'),
        follow_redirects=True)
    
    # Try registering with the same email address
    response = client.post('/register',
        data=dict(username='user3', password='345', confirm='345', name='User3'),
        follow_redirects=True)
    assert response.status_code == 200
    assert db.session.query(User).count() == 3
    assert b'This username is already taken. Try another one.' in response.data
    assert b'Login' in response.data
    assert b'Username' in response.data