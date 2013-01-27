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
    config.add_route('new-stamp-location', '/new-stamp-location')
    config.add_route('park', '/park/{park_url}')
    config.add_route('sign-up', '/sign-up')
    # Description here is for SEO value only and is ignored
    config.add_route('stamp-location', '/stamp-location/{description}/{stamp_location_id}')
    config.add_route('stamp-locations-json', '/stamp-locations.json')

def add_static_views(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('static/images', 'Parks:images', cache_max_age=3600)
