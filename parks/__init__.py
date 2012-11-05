from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings
from sqlalchemy import engine_from_config
from .models import DBSession
from .models import Base


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    session_factory = session_factory_from_settings(settings)

    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('static/images/', 'Parks:images', cache_max_age=3600)
    config.add_route('main', '/')
    config.add_route('park', '/park/{park_url}')
    config.set_session_factory(session_factory)
    config.scan()
    return config.make_wsgi_app()
