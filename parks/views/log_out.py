from pyramid.httpexceptions import HTTPFound
from pyramid.security import forget
from pyramid.view import view_config


@view_config(route_name='log-out')
def logout(request):
    headers = forget(request)
    return HTTPFound(
        location=request.route_url('home'),
        headers=headers,
    )
