from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
from pyramid.security import remember
from pyramid.view import view_config
from pyramid.view import forbidden_view_config

from parks.logic.security import check_login_and_get_user_id


@view_config(route_name='log-in', renderer='log_in.mako')
@forbidden_view_config(renderer='log_in.mako')
def log_in(request):
    render_dict = default_login_variables(request)
    return render_dict


@view_config(route_name='log-in-post', renderer='log_in.mako')
def log_in_post(request):
    referrer = request.url
    render_dict = default_login_variables(request)
    came_from = render_dict['came_from']

    if 'form.submitted' not in request.params:
        # How did we get to a POST endpoint without a form?
        render_dict.update(
            error="Sorry, there was an error submitting your login."
        )
        return render_dict

    login = request.params.get('login', '')
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
        username = authenticated_userid(request)
        if username is not None: # The user doesn't have the correct permissions
            render_dict.update(
                error="Sorry, you don't have permission to use this page."
            )
        elif referrer in (
            request.route_url('log-in'),
            request.route_url('log-in-post')
        ):
            render_dict.update(error='Your username or password was incorrect.')
        else:
            render_dict.update(info='Please log in to use this page.')

    return render_dict


def default_login_variables(request):
    """Returns a dict with login variables that should be shared between the
    GET and the POST (i.e. failed login) versions of the page.
    """
    referrer = request.url

    came_from = request.params.get('came-from', referrer)
    login_url = request.route_url('log-in')
    if came_from == login_url:
        # Never use the login form itself as came_from
        came_from = request.route_url('home')

    login = request.params.get('login', '')

    return {
        'post_url': request.route_url('log-in-post'),
        'came_from': came_from,
        'login': login,
    }
