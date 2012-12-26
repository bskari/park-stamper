from sqlalchemy import func

from parks.models import DBSession
from parks.models import Stamp
from parks.models import StampCollection
from parks.models import StampLocation
from parks.models import StampToLocation


def get_stamps_by_park_id(park_id):
    max_time_subquery = DBSession.query(
        StampCollection.stamp_id.label('stamp_id'),
        func.max(StampCollection.time_collected).label('most_recent_time'),
    ).group_by(
        StampCollection.stamp_id
    ).subquery()

    return DBSession.query(
        Stamp,
        StampLocation,
        max_time_subquery.c.most_recent_time,
    ).join(
        StampToLocation,
    ).join(
        StampLocation,
    ).outerjoin(
        max_time_subquery,
        Stamp.id == max_time_subquery.c.stamp_id,
    ).filter(
        StampLocation.park_id == park_id,
    ).all()
