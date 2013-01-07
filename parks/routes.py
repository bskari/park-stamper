"""Routes and static configuration.

Centralized here to make testing easier.
"""

def add_routes(config):
    config.add_route('all-parks', '/all-parks')
    config.add_route('home', '/')
    config.add_route('log-in', '/log-in')
    config.add_route('log-out', '/log-out')
    config.add_route('nearby', '/nearby')
    config.add_route('nearby-json', '/nearby.json')
    config.add_route('new-stamp', '/new-stamp')
    config.add_route('park', '/park/{park_url}')
    config.add_route('sign-up', '/sign-up')

def add_static_views(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('static/images', 'Parks:images', cache_max_age=3600)
