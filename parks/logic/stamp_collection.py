import datetime

from parks.models import DBSession
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
