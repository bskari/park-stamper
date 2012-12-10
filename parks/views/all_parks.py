from pyramid.view import view_config

from parks.models import DBSession
from parks.models import Park


@view_config(route_name='all_parks', renderer='all_parks.mako')
def all_parks(request):
    parks = DBSession.query(
        Park,
    ).all()

    return dict(parks=parks)
