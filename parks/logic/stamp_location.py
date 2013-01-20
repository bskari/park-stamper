from parks.models import DBSession
from parks.models import StampLocation
from parks.models import StampToLocation


def get_stamp_location_by_id(stamp_location_id):
    stamp_location = DBSession.query(
        StampLocation,
    ).filter(
        StampLocation.id == stamp_location_id
    ).one()

    return stamp_location


def get_stamp_locations_by_park_id(park_id):
    stamp_locations = DBSession.query(
        StampLocation
    ).filter(
        StampLocation.park_id == park_id
    ).all()

    return stamp_locations


def add_stamp_to_location(stamp_id, stamp_location_id):
    stamp_to_location = StampToLocation(
        stamp_id=stamp_id,
        stamp_location_id=stamp_location_id
    )

    DBSession.add(stamp_to_location)
