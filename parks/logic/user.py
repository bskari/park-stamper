from collections import namedtuple
from sqlalchemy.orm.exc import NoResultFound

from parks.models import DBSession
from parks.models import Park
from parks.models import StampCollection
from parks.models import User
from parks.models import UserEmail


def get_user_by_id(user_id):
    return DBSession.query(
        User,
    ).filter(
        User.id == user_id
    ).one()


def get_user_by_username_or_email(username_or_email):
    user = DBSession.query(
        User,
    ).filter(
        User.username == username_or_email
    ).all()

    if len(user) == 1:
        return user[0]

    user = DBSession.query(
        User,
    ).join(
        UserEmail,
        User.id == UserEmail.user_id
    ).filter(
        UserEmail.email == username_or_email
    ).all()

    if len(user) == 1:
        return user[0]

    raise NoResultFound('No user with that email or username was found')


def get_recent_user_collections(limit, after_date=None):
    """Returns up to limit recent stamp collections."""
    if limit > 10 or limit < 0:
        raise ValueError('Too much recent activity requested')

    # We need to load the various types of activity, then sort by the
    # time_created and just return a few items
    # TODO(bskari|2013-02-02) Load collection data
    CollectionNamedTuple = namedtuple(
        'CollectionNamedTuple',
        ['username', 'park_name', 'park_url']
    )
    query = DBSession.query(
        StampCollection.id,
        User,
        Park,
    ).join(
        User,
        User.id == StampCollection.user_id
    ).join(
        Park,
        Park.id == StampCollection.park_id
    )

    if after_date is not None:
        query = query.filter(StampCollection.date_collected > after_date)

    query = query.order_by(
        # id and time_created should be correlated
        StampCollection.id.desc()
    ).limit(
        limit
    )

    recent_collections = query.all()

    collections = [
        CollectionNamedTuple(
            rc.User.username,
            rc.Park.name,
            rc.Park.url
        )
        for rc in recent_collections
    ]
    return collections
