from parks.models import DBSession
from parks.models import User


def get_user_by_id(user_id):
    return DBSession.query(
        User,
    ).filter(
        User.id == user_id
    ).all()


def get_user_by_username(username):
    return DBSession.query(
        User,
    ).filter(
        User.username == username
    ).one()
