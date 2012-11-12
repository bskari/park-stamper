"""Routes and static configuration.

Centralized here to make testing easier.
"""

def add_routes(config):
    config.add_route('main', '/')
    config.add_route('park', '/park/{park_url}')

def add_static_views(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('static/images/', 'Parks:images', cache_max_age=3600)