"""
Test rooms.models.py.
"""
from rooms.models import User

def test_new_user():
    """
    GIVEN an User model
    WHEN a new User is created
    THEN check username, password is hashed, user is not anonymous
    """
    user = User('tommyboy', '123', 'TommyBoy')
    assert user.username == 'tommyboy'
    assert user.password != '123'
    assert not user.is_anonymous


def test_setting_password(new_user):
    """
    GIVEN an User model
    WHEN a new User is created
    THEN check the password is stored correctly and not as plaintext
    """
    new_user.set_password('TestPassword123')
    assert new_user.password != 'TestPassword123'
    assert new_user.check_password('TestPassword123')
    assert not new_user.check_password('TestPassword')

