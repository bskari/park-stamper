from collections import namedtuple
from pyramid.view import view_config

from parks.models import DBSession
from parks.models import Park


@view_config(route_name='all-parks', renderer='all_parks.mako')
def all_parks(request):
    parks = DBSession.query(
        Park.name,
        Park.region,
        Park.latitude,
        Park.longitude,
    ).all()
    ParkTuple = namedtuple('ParkTuple', ['name', 'region', 'latitude', 'longitude'])

    return dict(parks=parks)
