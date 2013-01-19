from parks.models import DBSession
from parks.models import Park
from parks.models import State


def get_all_parks():
    return DBSession.query(
        Park.name,
        Park.region,
        Park.latitude,
        Park.longitude,
        Park.url,
    ).order_by(
        Park.name
    ).all()


def get_all_park_names():
    parks = DBSession.query(
        Park.name
    ).order_by(
        Park.name
    ).all()

    return [i.name for i in parks]


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
