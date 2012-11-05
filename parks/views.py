from collections import namedtuple
import re

from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from .models import DBSession
from .models import Park


@view_config(route_name='main', renderer='home.mako')
def main(request):
    # TODO(bskari|2012-11-04) Load recent photos or something
    UrlAndCaption = namedtuple('UrlCaption', ['url', 'caption_header', 'caption'])
    carousel_image_urls_captions = [
        UrlAndCaption(
            request.static_url('Parks:images/home/parks/' + image),
            header,
            caption
        ) for image, header, caption in [
            (
                'delicate-arch.jpg',
                'Delicate Arch',
                'Arches National Park, Moab, Utah',
            ),
            (
                'grand-prismatic-spring.jpg',
                'Grand Prismatic Spring',
                'Yellowstone National Park, Jackson, Wyoming',
            ),
            (
                'colorado-dunes.jpg',
                'Dunes near Sangre de Cristo Mountains',
                'Great Sand Dunes National Park and Preserve, Alamosa, Colorado',
            ),
            (
                'dark-hollows-falls.jpg',
                'Dark Hollows Falls',
                'Shenandoah National Park, Waynesboro, Virginia',
            ),
            (
                'statue-of-liberty.jpg',
                'Statue of Liberty',
                'Statue of Liberty National Monument, New York City, New York',
            ),
            (
                'grand-tetons.jpg',
                'Grand Tetons',
                'Grand Tetons National Park, Jackson, Wyoming',
            ),
        ]
    ]
    return dict(
        carousel_image_urls_captions=carousel_image_urls_captions
    )


@view_config(route_name='park', renderer='park.mako')
def park(request):
    park_url = request.matchdict['park_url']
    park = DBSession.query(Park).filter_by(url=park_url).first()
    if park is None:
        return HTTPNotFound('No park found')

    # Stamp info
    return dict(park=park)
