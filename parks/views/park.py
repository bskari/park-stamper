from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

from parks.models import DBSession
from parks.models import Park


@view_config(route_name='park', renderer='park.mako')
def park(request):
    park_url = request.matchdict['park_url']
    park = DBSession.query(Park).filter_by(url=park_url).first()
    if park is None:
        return HTTPNotFound('No park found')

    # Stamp info
    return dict(park=park)
