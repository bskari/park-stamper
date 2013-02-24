import datetime

from parks.models import DBSession
from parks.models import Park
from parks.models import Stamp
from parks.models import StampCollection


def collect_stamp(user_id, stamp_id, park_id, date=None):
    if date is None:
        date = datetime.date.today()

    collection = StampCollection(
        user_id=user_id,
        stamp_id=stamp_id,
        park_id=park_id,
        date_collected=date
    )

    DBSession.add(collection)


def get_recent_collections_by_user_id(user_id, days_ago):
    from_date = datetime.datetime.today() - datetime.timedelta(days=days_ago)

    recent = DBSession.query(
        StampCollection,
        Stamp,
        Park
    ).join(
        Stamp,
        Stamp.id == StampCollection.stamp_id
    ).join(
        Park,
        Park.id == StampCollection.park_id
    ).filter(
        StampCollection.user_id == user_id
    ).filter(
        StampCollection.date_collected >= from_date
    ).order_by(
        StampCollection.date_collected.desc()
    ).all()

    return recent
