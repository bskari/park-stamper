from collections import namedtuple
import datetime
from pyramid.view import view_config

from parks.logic import user as user_logic


@view_config(route_name='home', renderer='home.mako')
def home(request):
    carousel_information = _get_static_carousel_information(request)
    two_weeks_ago = datetime.datetime.today() - datetime.timedelta(days=14)
    recent = user_logic.get_recent_user_collections(5, two_weeks_ago)
    return dict(
        carousel_information=carousel_information,
        urls=dict(nearby=request.route_url('nearby')),
        recent=recent,
    )


def _get_static_carousel_information(request):
    CarouselInformation = namedtuple(
        'CarouselInformation',
        ['img_url', 'header', 'caption', 'url']
    )
    carousel_information = [
        CarouselInformation(
            # TODO(bskari|2012-11-04) Load recent photos or something
            request.static_url('Parks:images/home/parks/' + image),
            header,
            caption,
            request.route_url('park', park_url=url),
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
                'Grand Teton',
                'Grand Teton National Park, Jackson, Wyoming',
                'grand-teton',
            ),
        ]
    ]
    return carousel_information
