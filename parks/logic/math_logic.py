from math import cos
from math import pi
from math import sqrt

EARTH_RADIUS = 3961.0


def latitude_to_miles(latitude=None, longitude=None):
    return EARTH_RADIUS * pi / 180.0


def longitude_to_miles(latitude, longitude=None):
    return abs(cos(latitude) * latitude_to_miles())


def latitude_longitude_distance(
    source_latitude,
    source_longitude,
    destination_latitude,
    destination_longitude,
):
    x_difference = destination_longitude - source_longitude
    y_difference = destination_latitude - source_latitude

    x = longitude_to_miles((source_latitude + destination_latitude) / 2) * x_difference
    y = latitude_to_miles() * y_difference

    return sqrt(x * x + y * y)
