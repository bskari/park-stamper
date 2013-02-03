from collections import namedtuple
from sqlalchemy import distinct

from parks.models import DBSession
from parks.models import Park
from parks.models import StampCollection
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


def get_recent_user_collections(limit):
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
    recent_collections = DBSession.query(
        StampCollection.id,
        User,
        Park,
    ).join(
        User,
        User.id == StampCollection.user_id
    ).join(
        Park,
        Park.id == StampCollection.park_id
    ).order_by(
        # id and time_created should be correlated
        StampCollection.id.desc()
    ).limit(
        limit
    ).all()

    collections = [
        CollectionNamedTuple(
            rc.User.username,
            rc.Park.name,
            rc.Park.url
        )
        for rc in recent_collections
    ]
    return collections
