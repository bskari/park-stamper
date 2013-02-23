from sqlalchemy import asc
from sqlalchemy import func

from parks.logic.math_logic import latitude_to_miles
from parks.logic.math_logic import latitude_longitude_distance
from parks.logic.math_logic import longitude_to_miles
from parks.models import DBSession
from parks.models import Park
from parks.models import Stamp
from parks.models import StampCollection
from parks.models import StampLocation
from parks.models import StampToLocation


def get_stamps_by_park_id(park_id):
    max_time_subquery = DBSession.query(
        StampCollection.stamp_id.label('stamp_id'),
        func.max(StampCollection.date_collected).label('most_recent_time'),
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
    ).group_by(
        Stamp.id
    ).all()


def get_stamps_by_location_id(location_id):
    max_time_subquery = DBSession.query(
        StampCollection.stamp_id.label('stamp_id'),
        func.max(StampCollection.date_collected).label('most_recent_time'),
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
        StampLocation.id == location_id,
    ).group_by(
        Stamp.id
    ).all()


def get_nearby_stamps(latitude, longitude, distance_miles):
    lower_latitude = latitude - (distance_miles / latitude_to_miles())
    upper_latitude = latitude + (distance_miles / latitude_to_miles())
    lower_longitude = longitude - (distance_miles / longitude_to_miles(longitude))
    upper_longitude = longitude + (distance_miles / longitude_to_miles(longitude))

    max_time_subquery = DBSession.query(
        StampCollection.stamp_id.label('stamp_id'),
        func.max(StampCollection.date_collected).label('most_recent_time'),
    ).join(
        Stamp
    ).group_by(
        StampCollection.stamp_id
    ).subquery()

    stamps = DBSession.query(
        StampLocation,
        Stamp,
        Park,
        max_time_subquery.c.most_recent_time.label('last_seen'),
    ).join(
        StampToLocation
    ).join(
        Stamp
    ).join(
        Park
    ).outerjoin(
        max_time_subquery,
        max_time_subquery.c.stamp_id == Stamp.id
    ).filter(
        StampLocation.latitude.between(lower_latitude, upper_latitude)
    ).filter(
        StampLocation.longitude.between(lower_longitude, upper_longitude)
    ).order_by(
        asc(
            (latitude - StampLocation.latitude) * (latitude - StampLocation.latitude) +
            (longitude - StampLocation.longitude) * (longitude - StampLocation.longitude)
        )
    ).all()

    # We're doing square distance calculation in SQL so that we can use
    # indexes, so we might include some stamps that aren't within the radius
    # that we need to post-filter
    stamps = [
        s for s in stamps if latitude_longitude_distance(
            latitude,
            longitude,
            s.StampLocation.latitude,
            s.StampLocation.longitude
        ) < distance_miles
    ]

    return stamps


def stamp_exists(stamp_text):
    stamp_text_count = DBSession.query(
        Stamp.text
    ).filter(
        Stamp.text == stamp_text
    ).count()

    if stamp_text_count > 0:
        return True
    else:
        return False


def create_new_stamp(stamp_text, stamp_type, added_by_user_id):
    # The model allows for nulls here because my initial database population
    # script doesn't have a user, so just enforce this rule here
    if added_by_user_id is None:
        raise ValueError('added_by_user should not be None')

    stamp = Stamp(
        text=stamp_text,
        type=stamp_type,
        status='active',
        added_by_user_id=added_by_user_id,
    )
    DBSession.add(stamp)

    stamp_id = DBSession.query(
        Stamp.id
    ).filter(
        Stamp.text == stamp_text
    ).one()

    return stamp_id[0]


def get_stamps_beginning_with_string(text, limit=None):
    """Returns stamps with text that start with the substring."""
    if limit is None:
        limit = 10

    stamps = DBSession.query(
        Stamp
    ).filter(
        Stamp.text.like(text + '%')
    ).limit(
        limit
    ).all()

    return stamps
