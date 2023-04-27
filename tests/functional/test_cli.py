"""
This file (test_cli.py) contains the functional tests for the CLI functions.
"""
from rooms import db
from rooms.models import User, Topic, Room, Message

def test_import_test_data(runner):
    """
    GIVEN a Flask application configured for testing
    WHEN the 'flask import_data' command is called from the command line
    THEN check the response is valid
    """
    
    result = runner.invoke(args=['import_data'])

    assert result.exit_code == 0
    assert 'All test data is added successfully.' in result.output
    assert db.session.query(User).count() > 2
    assert db.session.query(Topic).count() > 2
    assert db.session.query(Room).count() > 2
    assert db.session.query(Message).count() > 2
