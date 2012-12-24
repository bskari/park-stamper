from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.events import BeforeRender
from pyramid.security import authenticated_userid
from pyramid_beaker import session_factory_from_settings
from sqlalchemy import engine_from_config

from parks.models import DBSession
from parks.models import Base
from parks.routes import add_routes
from parks.routes import add_static_views
from parks.security import group_finder


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    session_factory = session_factory_from_settings(settings)

    config = Configurator(
        settings=settings,
        root_factory='parks.security.RootFactory',
    )

    # Authentication
    authn_policy = AuthTktAuthenticationPolicy(
        'b5kUolGpl79YxIWqzaNKedhtv7yEi7c6lAcbdBYi',
        callback=group_finder,
    )
    config.set_authentication_policy(authn_policy)
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)

    # Rendering policies
    config.add_subscriber(add_renderer_globals, BeforeRender)

    # Routes
    add_routes(config)
    add_static_views(config)

    # Sessions
    config.set_session_factory(session_factory)

    config.scan()
    return config.make_wsgi_app()


def add_renderer_globals(event):
    """Update the render dictionary with globals for every page."""
    event['user_id'] = authenticated_userid(event['request'])
