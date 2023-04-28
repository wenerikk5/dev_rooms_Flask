# dev_rooms_Flask

## Description

Copy of my dev_rooms project developed early on Django.

A draft of public site for devs to discuss different topics related with programming languages. Has been built on Flask with Jinja2 Templates + Flask SQLAlchemy + Alembic + Flask-Login + Bootstrap styling. Main functionality has been covered by Pytests (84% coverage).

## Set up and use

All commands should be executed from main directory (dev_rooms_Flask)

```
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt

# Rename and update (at least SECRET_KEY) .env-example file to .env
mv .env-example .env

# OPTIONAL: commands to handle migrations (initiate, update).  
# NOTE: Update works only for adding and removing of exist tables fields 
# and do not handle renaming of exist fields.
flask db init 
flask db migrate
flask db update

# OPTIONAL: Fill database with test data (for all tables). 
# NOTE: Before filling run server at least once in order to create database file.
flask import_data # adds (in order) users, topics, rooms and messages.

# Run server (default in Debug mode)
flask run # make sure that .env file is in place

# Stop server with Ctrl + C

# Test user data:
# Username: mike
# Password: Abc123123

```

## Testing

```
# Run Pytests in verbose mode
python -m pytest -v

# Coverage
python -m pytest --cov-report term-missing --cov=rooms
```

## Additional info

Created for educational purposes. 

## Preview
<img src="https://github.com/wenerikk5/dev_rooms_Flask/blob/7ff2b002b5f95f879b31ba863e07e3038a14e7b3/rooms/static/uploads/base/Preview.png" alt="img" width="800" height='600'>


