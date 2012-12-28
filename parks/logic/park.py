from parks.models import DBSession
from parks.models import Park
from parks.models import State


def get_all_parks():
    return DBSession.query(
        Park.name,
        Park.region,
        Park.latitude,
        Park.longitude,
    ).all()


def get_park_and_state_by_url(park_url):
    return DBSession.query(
        Park,
        State,
    ).join(
        State,
        Park.state_id == State.id
    ).filter(
        Park.url == park_url
    ).all()