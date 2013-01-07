from sqlalchemy import asc
from sqlalchemy import func

from parks.models import DBSession
from parks.models import Park
from parks.models import Stamp
from parks.models import StampLocation
from parks.models import StampToLocation


def get_stamp_location_by_id(stamp_location_id):
    stamp_location = DBSession.query(
        StampLocation,
        Park
    ).filter(
        StampLocation.id == stamp_location_id
    ).first()

    return stamp_location

def add_stamp_to_location(stamp_id, stamp_location_id):
    stamp_to_location = StampToLocation(
        stamp_id=stamp_id,
        stamp_location_id=stamp_location_id
    )

    DBSession.add(stamp_to_location)
