from sqlalchemy import distinct
from sqlalchemy import func

from parks.models import DBSession
from parks.models import Park
from parks.models import StampCollection
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


def get_park_by_id(id):
    park = DBSession.query(
        Park
    ).filter(
        Park.id == id
    ).one()

    return park


def get_park_by_name(name):
    park = DBSession.query(
        Park
    ).filter(
        Park.name == name
    ).one()

    return park


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


def count_parks_visited_by_user_id(user_id):
    """Returns the count of the parks that a user has visited."""
    counts = DBSession.query(
        func.count(distinct(StampCollection.park_id))
    ).filter(
        StampCollection.user_id == user_id
    ).one()[0]

    return counts


def count_parks_by_region_visited_by_user_id(user_id):
    count_function = func.count(distinct(StampCollection.park_id))
    regions_and_counts = DBSession.query(
        Park.region,
        count_function,
    ).filter(
        Park.id == StampCollection.park_id
    ).filter(
        StampCollection.user_id == user_id
    ).order_by(
        count_function.desc()
    ).group_by(
        Park.region
    ).all()
    import pdb; pdb.set_trace()

    all_regions = set(Park.region.property.columns[0].type.enums)
    visited_regions = set([region for region, _ in regions_and_counts])
    unvisited_regions = all_regions - visited_regions
    for region in unvisited_regions:
        regions_and_counts.append((region, 0))
    return regions_and_counts


def count_parks():
    return DBSession.query(func.max(Park.id)).one()[0]
