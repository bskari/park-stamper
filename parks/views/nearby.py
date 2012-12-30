import datetime
from pyramid.url import route_url
from pyramid.view import view_config


@view_config(route_name='nearby', renderer='nearby.mako')
def nearby(request):
    return dict(csrf_token=request.session.get_csrf_token())


@view_config(route_name='nearby_json', renderer='json')
def nearby_json(request):
    latitude = request.GET.get('latitude', None)
    longitude = request.GET.get('longitude', None)
    if latitude is None or longitude is None:
        return dict(success=False, error='No latitude or longitude provided')

    now = datetime.datetime.now().isoformat()

    return dict(
        success=True,
        stamps=[
            dict(
                park='Yellowstone',
                url=route_url('park', request, park_url='yellowstone'),
                text='Test Data\nYellowstone National Park',
                location='Visitor Center',
                coordinates=dict(latitude=37.774, longitude=-122.419),
                distance=1.2,
                last_seen=now,
            ),
            dict(
                park='Yellowstone',
                url=route_url('park', request, park_url='yellowstone'),
                text='Test Data 2\nYellowstone National Park',
                location='Visitor Center',
                coordinates=dict(latitude=37.774, longitude=-122.419),
                distance=1.2,
                last_seen=now,
            ),
        ],
    )
