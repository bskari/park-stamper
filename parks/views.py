from collections import namedtuple
import re

from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from .models import DBSession
from .models import Park


@view_config(route_name='main', renderer='home.mako')
def main(request):
    CarouselInformation = namedtuple(
        'CarouselInformation',
        ['img_url', 'header', 'caption', 'url']
    )
    carousel_information = [
        CarouselInformation(
            request.static_url('Parks:images/home/parks/' + image),
            header,
            caption,
            request.route_url('park', park_url=url),
        # TODO(bskari|2012-11-04) Load recent photos or something
        ) for image, header, caption, url in [
            (
                'delicate-arch.jpg',
                'Delicate Arch',
                'Arches National Park, Moab, Utah',
                'arches',
            ),
            (
                'grand-prismatic-spring.jpg',
                'Grand Prismatic Spring',
                'Yellowstone National Park, Jackson, Wyoming',
                'yellowstone',
            ),
            (
                'colorado-dunes.jpg',
                'Dunes near Sangre de Cristo Mountains',
                'Great Sand Dunes National Park and Preserve, Alamosa, Colorado',
                'great-sand-dunes',
            ),
            (
                'dark-hollows-falls.jpg',
                'Dark Hollows Falls',
                'Shenandoah National Park, Waynesboro, Virginia',
                'shenandoah',
            ),
            (
                'statue-of-liberty.jpg',
                'Statue of Liberty',
                'Statue of Liberty National Monument, New York City, New York',
                'statue-of-liberty',
            ),
            (
                'grand-tetons.jpg',
                'Grand Tetons',
                'Grand Tetons National Park, Jackson, Wyoming',
                'grand-tetons',
            ),
        ]
    ]
    return dict(
        carousel_information=carousel_information,
    )


@view_config(route_name='park', renderer='park.mako')
def park(request):
    park_url = request.matchdict['park_url']
    park = DBSession.query(Park).filter_by(url=park_url).first()
    if park is None:
        return HTTPNotFound('No park found')

    # Stamp info
    return dict(park=park)
