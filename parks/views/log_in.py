from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
from pyramid.security import remember
from pyramid.view import view_config
from pyramid.view import forbidden_view_config

from parks.logic.security import check_login_and_get_user_id


@view_config(route_name='log-in', renderer='log_in.mako')
@forbidden_view_config(renderer='log_in.mako')
def log_in(request):
    login_url = request.route_url('log-in')
    referrer = request.url
    came_from = request.params.get('came-from', referrer)
    if came_from == login_url:
        # Never use the login form itself as came_from
        came_from = request.route_url('home')
    login = ''
    render_dict = {}

    if 'form.submitted' in request.params:
        login = request.params.get('login', None)
        password = request.params.get('password', None)
        user_id = check_login_and_get_user_id(login, password)
        if user_id is not None:
            headers = remember(request, user_id)
            # Redirect back to the page the user came from
            return HTTPFound(
                location=came_from,
                headers=headers,
            )
        else:
            render_dict.update(error='Invalid username or password.')

    if render_dict.get('error', None) is None:
        username = authenticated_userid(request)
        if username is not None:
            render_dict.update(error="Sorry, you don't have permission to use this page.")
        elif referrer != request.route_url('log-in'):
            render_dict.update(info='Please log in to use this page.')

    render_dict.update(
        url=request.route_url('log-in'),
        came_from=came_from,
        login=login,
    )

    return render_dict
