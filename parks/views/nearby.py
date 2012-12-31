from math import pi
from math import tan
from pyramid.view import view_config

from parks.logic.stamp import get_nearby_stamps


@view_config(route_name='nearby', renderer='nearby.mako')
def nearby(request):
    return dict(csrf_token=request.session.get_csrf_token())


@view_config(route_name='nearby_json', renderer='json')
def nearby_json(request):
    latitude = request.GET.get('latitude', None)
    longitude = request.GET.get('longitude', None)
    distance = request.GET.get('distance', None)
    if latitude is None or longitude is None:
        return dict(success=False, error='No latitude or longitude provided')

    latitude = float(latitude)
    longitude = float(longitude)
    if distance is not None:
        distance = float(distance)
    else:
        distance = 50

    if distance > 100:
        return dict(
            success=False,
            error='Radius is too large'
        )

    nearby_stamps = get_nearby_stamps(latitude, longitude, distance)

    def direction(
        source_latitude,
        source_longitude,
        destination_latitude,
        destination_longitude,
    ):
        x = destination_longitude - source_longitude
        y = destination_latitude - source_latitude
        angle = tan(y / x) * pi
        if angle < 0:
            angle += 360
        if angle <= 22.5:
            return 'n'
        elif 22.5 < angle <= 67.5:
            return 'ne'
        elif 67.5 < angle <= 112.5:
            return 'e'
        elif 112.5 < angle <= 157.5:
            return 'se'
        elif 157.5 < angle <= 202.5:
            return 's'
        elif 202.5 < angle <= 247.5:
            return 'sw'
        elif 247.5 < angle <= 292.5:
            return 'w'
        elif 292.5 < angle <= 337.5:
            return 'nw'
        else:
            return 'n'

    stamp_info = [
        dict(
            park=s.Park.name,
            url=request.route_url('park', park_url=s.Park.url),
            text=s.Stamp.text,
            location=(
                s.StampLocation.description
                if s.StampLocation.description is not None
                else 'Unknown'
            ),
            coordinates=dict(
                latitude=s.StampLocation.latitude,
                longitude=s.StampLocation.longitude,
            ),
            distance=0.0, #TODO
            last_seen='never', #TODO
            direction=direction(
                latitude,
                longitude,
                s.StampLocation.latitude,
                s.StampLocation.longitude,
            ),
        )
        for s in nearby_stamps
    ]


    return dict(
        success=True,
        stamps=stamp_info,
    )
