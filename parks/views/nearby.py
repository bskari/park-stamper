from pyramid.view import view_config


@view_config(route_name='nearby', renderer='nearby.mako')
def nearby(request):
    return dict()
