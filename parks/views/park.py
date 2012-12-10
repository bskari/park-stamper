from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from sqlalchemy import func

from parks.models import DBSession
from parks.models import Park
from parks.models import Stamp
from parks.models import StampCollection
from parks.models import StampLocation
from parks.models import StampToLocation
from parks.models import State


@view_config(route_name='park', renderer='park.mako')
def park(request):
    park_url = request.matchdict['park_url']
    results = DBSession.query(
        Park,
        State,
    ).join(
        State,
        Park.state_id == State.id
    ).filter(
        Park.url == park_url
    ).all()

    if len(results) == 0:
        return HTTPNotFound('No park found')
    if len(results) != 1:
        return HTTPNotFound('Internal error: multiple parks found')
    park, state = results[0]


    max_time_subquery = DBSession.query(
        StampCollection.stamp_id.label('stamp_id'),
        func.max(StampCollection.time_collected).label('most_recent_time'),
    ).group_by(
        StampCollection.stamp_id
    ).subquery()

    stamps = DBSession.query(
        Stamp,
        StampLocation,
        max_time_subquery.c.most_recent_time,
    ).join(
        StampToLocation,
    ).join(
        StampLocation,
    ).outerjoin(
        max_time_subquery,
        Stamp.id == max_time_subquery.c.stamp_id,
    ).filter(
        StampLocation.park_id == park.id,
    ).all()

    return dict(park=park, state=state, stamps=stamps)
