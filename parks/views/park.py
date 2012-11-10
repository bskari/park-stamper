from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

from parks.models import DBSession
from parks.models import Park
from parks.models import Stamp
from parks.models import StampCollection


@view_config(route_name='park', renderer='park.mako')
def park(request):
    park_url = request.matchdict['park_url']
    park = DBSession.query(Park).filter_by(url=park_url).first()
    if park is None:
        return HTTPNotFound('No park found')

    statement = DBSession.query(
        StampCollection.id.label('stamp_id'),
        StampCollection.time_collected.label('most_recent_collection_time'),
    ).order_by(
        StampCollection.time_collected.desc(),
    ).limit(
        1
    ).subquery()

    stamps = DBSession.query(
        Stamp,
        statement.c.most_recent_collection_time,
    ).outerjoin(
        statement,
        Stamp.id == statement.c.stamp_id,
    ).filter(
        Stamp.park_id == park.id,
    ).all()

    # Stamp info
    return dict(park=park, stamps=stamps)
