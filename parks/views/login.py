from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.view import view_config
from pyramid.view import forbidden_view_config

from parks.logic.security import check_login_and_get_username


@view_config(route_name='login', renderer='login.mako')
@forbidden_view_config(renderer='login.mako')
def login(request):
    login_url = request.route_url('login')
    referrer = request.url
    came_from = request.params.get('came_from', referrer)
    if came_from == login_url:
        # Never use the login form itself as came_from
        came_from = request.route_url('main')
    login = ''
    render_dict = {}

    if 'form.submitted' in request.params:
        login = request.params.get('login', None)
        password = request.params.get('password', None)
        username = check_login_and_get_username(login, password)
        if username is not None:
            headers = remember(request, login)
            # Redirect back to the page the user came from
            return HTTPFound(
                location=came_from,
                headers=headers,
            )
        else:
            render_dict.update(error='Invalid username or password.')

    render_dict.update(
        url=request.application_url + '/login',
        came_from=came_from,
        login=login,
    )

    return render_dict
