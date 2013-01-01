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


def get_nearby_stamps(latitude, longitude, distance_miles):
    lower_latitude = latitude - (distance_miles / latitude_to_miles())
    upper_latitude = latitude + (distance_miles / latitude_to_miles())
    lower_longitude = longitude - (distance_miles / longitude_to_miles(longitude))
    upper_longitude = longitude + (distance_miles / longitude_to_miles(longitude))

    stamps = DBSession.query(
        StampLocation,
        Stamp,
        Park
    ).join(
        StampToLocation
    ).join(
        Stamp
    ).join(
        Park
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
