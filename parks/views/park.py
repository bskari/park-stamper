from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from sqlalchemy import func

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

    max_time_subquery = DBSession.query(
        StampCollection.stamp_id.label('stamp_id'),
        func.max(StampCollection.time_collected).label('most_recent_time'),
    ).group_by(
        StampCollection.stamp_id
    ).subquery()

    stamps = DBSession.query(
        Stamp,
        max_time_subquery.c.most_recent_time,
    ).outerjoin(
        max_time_subquery,
        Stamp.id == max_time_subquery.c.stamp_id,
    ).filter(
        Stamp.park_id == park.id,
    ).all()

    # Stamp info
    return dict(park=park, stamps=stamps)
