from pyramid.view import view_config

import parks.logic.park as park_logic


@view_config(route_name='all-parks', renderer='all_parks.mako')
def all_parks(request):
    parks = park_logic.get_all_parks()

    return dict(parks=parks)
