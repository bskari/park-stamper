import logging
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.events import BeforeRender
from pyramid.events import NewRequest
from pyramid.security import authenticated_userid
from pyramid_beaker import session_factory_from_settings
from sqlalchemy import engine_from_config

from parks.logic.security import group_finder
from parks.models import DBSession
from parks.models import Base
from parks.routes import add_routes
from parks.routes import add_static_views

logger = logging.getLogger(__name__)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    session_factory = session_factory_from_settings(settings)

    config = Configurator(
        settings=settings,
        root_factory='parks.logic.security.RootFactory',
    )

    # Authentication
    authn_policy = AuthTktAuthenticationPolicy(
        settings['authn_key'],
        callback=group_finder,
        hashalg='sha512',
    )
    config.set_authentication_policy(authn_policy)
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)

    # Rendering policies
    config.include('pyramid_mako')
    config.add_subscriber(add_renderer_globals, BeforeRender)
    config.add_subscriber(csrf_validation_event, NewRequest)

    # Routes
    add_routes(config)
    add_static_views(config)

    # Sessions
    config.set_session_factory(session_factory)

    config.scan()
    return config.make_wsgi_app()


def add_renderer_globals(event):
    """Update the render dictionary with globals for every page."""
    request = event['request']
    event['user_id'] = authenticated_userid(request)
    event['csrf_token'] = request.session.get_csrf_token()


def csrf_validation_event(event):
    """Checks CSRF tokens on all POST requests and aborts the request if
    validation fails.
    """
    request = event.request

    # We only need to CSRF validate POST and XHR requests
    if request.method != 'POST' and not request.is_xhr:
        return

    # CSRF tokens could come from AJAX where you're supposed to have JSON
    # encoded parameters (which use camelCase) or from form inputs (which use
    # dashed-names) so just try both.
    csrf_token = request.params.get('csrfToken', None)
    if csrf_token is None:
        csrf_token = request.params.get('csrf-token', None)

    if csrf_token is None:
        logger.warn('No CSRF token found for request {0}'.format(request))
        return HTTPUnauthorized
    elif csrf_token != str(request.session.get_csrf_token()):
        logger.warn('Invalid CSRF token found for request {0}'.format(request))
        raise HTTPUnauthorized
