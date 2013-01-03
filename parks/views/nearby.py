from math import pi
from math import atan
from pyramid.view import view_config

from parks.logic.math_logic import latitude_longitude_distance
import parks.logic.stamp


@view_config(route_name='nearby', renderer='nearby.mako')
def nearby(request):
    return dict(csrf_token=request.session.get_csrf_token())


@view_config(route_name='nearby-json', renderer='json')
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

    nearby_stamps = parks.logic.stamp.get_nearby_stamps(latitude, longitude, distance)

    def direction(
        source_latitude,
        source_longitude,
        destination_latitude,
        destination_longitude,
    ):
        x = float(destination_longitude - source_longitude)
        y = float(destination_latitude - source_latitude)
        if y == 0:
            y = 0.00000001
        angle = abs(atan(x / y) * 180 / pi)

        if destination_latitude >= source_latitude:
            above = True
        else:
            above = False

        if destination_longitude >= source_longitude:
            right = True
        else:
            right = False

        if above and right: # Quadrant I
            pass
        elif not above and right: # Quadrant II
            angle = 180 - angle
        elif not above and not right: # Quadrant III
            angle += 180
        else: # Quadrant IV
            angle = 360 - angle

        if angle <= 22.5:
            return 'north'
        elif 22.5 < angle <= 67.5:
            return 'northeast'
        elif 67.5 < angle <= 112.5:
            return 'east'
        elif 112.5 < angle <= 157.5:
            return 'southeast'
        elif 157.5 < angle <= 202.5:
            return 'south'
        elif 202.5 < angle <= 247.5:
            return 'southwest'
        elif 247.5 < angle <= 292.5:
            return 'west'
        elif 292.5 < angle <= 337.5:
            return 'northwest'
        else:
            return 'north'

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
            distance=latitude_longitude_distance(
                latitude,
                longitude,
                s.StampLocation.latitude,
                s.StampLocation.longitude,
            ),
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
