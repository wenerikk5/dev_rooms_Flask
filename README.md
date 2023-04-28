# dev_rooms_on_Flask

## Description

Copy of my dev_rooms project developed early on Django.

A draft of public site for devs to discuss different topics related with programming languages. Has been built on Flask with Jinja2 Templates + Flask SQLAlchemy + Alembic + Flask-Login + Bootstrap styling. Main functionality has been covered by Pytests (84% coverage).

## Set up and use

```
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt

# Rename and update (at least SECRET_KEY) .env-example file to .env
mv .env-example .env

# OPTIONAL: commands to handle migrations (initiate, update).  
# NOTE. Update works only for adding and removing of exist tables fields and do not handle renaming of exist fields.
falsk db init 
flask db migrate
flask db update

# OPTIONAL: Fill database with test data (for all tables)
flask import_data # adds (in order) users, topics, rooms and messages.

# Run server (default in Debug mode)
flask run # make sure that .env file is in place

# Test user data:
# Username: mike
# Password: Abc123123

```

## Additional info

Created for educational purposes. 

## Preview
<img src="https://github.com/wenerikk5/dev_rooms/blob/06d2abc16d5cbdbf38f508d0ce39be0b6125d029/media/base/Preview.png" alt="img" width="800" height='600'>

