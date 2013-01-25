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


def stamp_location_exists(park_id, description):
    description_count = DBSession.query(
        StampLocation.park_id
    ).filter(
        StampLocation.park_id == park_id
    ).filter(
        StampLocation.description == description
    ).count()

    if description_count > 0:
        return True
    else:
        return False


def create_new_stamp_location(park_id, description, address, latitude, longitude):
    stamp_location = StampLocation(
        park_id=park_id,
        description=description,
        address=address,
        latitude=latitude,
        longitude=longitude,
    )
    DBSession.add(stamp_location)

    stamp_location_id = DBSession.query(
        StampLocation.id
    ).filter(
        StampLocation.park_id == park_id
    ).filter(
        StampLocation.description == description
    ).one()

    return stamp_location_id[0]
