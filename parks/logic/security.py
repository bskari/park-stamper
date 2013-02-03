from bcrypt import hashpw
from pyramid.security import Allow
from pyramid.security import Everyone
from sqlalchemy import or_

from parks.models import DBSession
from parks.models import User
from parks.models import UserEmail


class RootFactory(object):
    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, 'group:users', 'edit'),
    ]

    def __init__(self, request):
        pass


def group_finder(username, request):
    """Returns a list of group identifiers that the user belongs to, or None
    if the user doesn't belong to any groups.
    
    Right now, I don't have any group specific privileges, so just return that
    the user is a member of the 'users' group.
    """
    if username is not None:
        return ['group:users']
    else:
        return None


def check_login_and_get_username(login, password):
    """Checks a provided login (either username or email address) and if there
    is a user with those credentials, returns that user's username.
    """
    possible_logins = DBSession.query(
        User.username,
        User.password,
    ).outerjoin(
        UserEmail
    ).filter(
        or_(
            User.username == login,
            UserEmail.email == login,
        )
    ).all()

    if len(possible_logins) > 1:
        raise AssertionError('Multiple logins found')
    if len(possible_logins) == 0:
        return None
    login = possible_logins[0]
    if login.password == hashpw(password, login.password):
        return login.username
