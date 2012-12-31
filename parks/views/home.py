from collections import namedtuple

from pyramid.view import view_config


@view_config(route_name='home', renderer='home.mako')
def home(request):
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
                'Grand Teton',
                'Grand Teton National Park, Jackson, Wyoming',
                'grand-teton',
            ),
        ]
    ]
    return dict(
        carousel_information=carousel_information,
        urls=dict(nearby=request.route_url('nearby')),
    )
