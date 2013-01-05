from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.view import view_config

from parks.models import DBSession as session
from parks.models import User
from parks.models import UserEmail


@view_config(route_name='sign-up', renderer='sign_up.mako')
def sign_up(request):
    sign_up_url = request.route_url('sign-up')
    referrer = request.url
    came_from = request.params.get('came_from', referrer)
    if came_from == sign_up_url:
        # Never use the sign_up_url form itself as came_from
        came_from = request.route_url('home')
    render_dict = {}

    if 'form.submitted' in request.params:
        username = request.params.get('username', None)
        email = request.params.get('email', None)
        password = request.params.get('password', None)

        # Use a fake loop so that I can break out early on errors
        for _ in xrange(1):
            if '@' not in email or len(email) < 5:
                render_dict.update(error="Your email doesn't look quite right.")
                break

            emails = session.query(
                UserEmail.email
            ).filter(
                UserEmail.email == email
            ).count()

            if emails != 0:
                render_dict.update(error='That email address is already in use.')
                break

            usernames = session.query(
                User
            ).filter(
                User.username == username
            ).count()

            if usernames != 0:
                render_dict.update(error='That username is already in use.')
                break

            if password is None:
                render_dict.update(error='No password entered.')
                break
            if username is None:
                render_dict.update(error='No username entered.')
                break

            user = User(
                username=username,
                password=password,
                signup_ip=request.client_addr,
            )
            session.add(user)
            user_email = UserEmail(username, email)
            session.add(user_email)

            headers = remember(request, username)

            # Redirect back to the page the user came from
            return HTTPFound(
                location=came_from,
                headers=headers,
            )

    render_dict.update(
        url=sign_up_url,
        came_from=came_from,
    )

    return render_dict
