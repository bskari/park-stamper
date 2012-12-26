from pyramid.view import view_config

from parks.logic.park import get_all_parks


@view_config(route_name='all-parks', renderer='all_parks.mako')
def all_parks(request):
    parks = get_all_parks()

    return dict(parks=parks)
