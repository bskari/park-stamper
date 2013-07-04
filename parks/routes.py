"""Routes and static configuration.

Centralized here to make testing easier.
"""

def add_routes(config):
    # GETs
    for name, pattern in (
        ('add-stamp-to-location', '/add-stamp-to-location'),
        ('all-parks', '/all-parks'),
        ('home', '/'),
        ('log-in', '/log-in'),
        ('log-out', '/log-out'),
        ('nearby', '/nearby'),
        ('nearby-json', '/nearby.json'),
        ('new-stamp', '/new-stamp'),
        ('new-stamp-location', '/new-stamp-location'),
        ('park', '/park/{park_url}'),
        ('park-names-json', '/park-names.json'),
        ('profile-personal', '/profile/'),
        ('profile-user', '/profile/{username}'),
        ('sign-up', '/sign-up'),
        # Park here is for SEO value only and is ignored
        ('stamp-location', '/stamp-location/{id}/{park}'),
        ('stamp-locations-json', '/stamp-locations.json'),
        ('stamps-substring-json', '/stamps-substring.json'),
    ):
        config.add_route(name, pattern, request_method='GET')

    # POSTs
    for name, pattern in (
        ('add-stamp-to-location-post', '/add-stamp-to-location'),
        ('collect-stamp', '/collect-stamp'),
        ('log-in-post', '/log-in-post'),
        ('new-stamp-post', '/new-stamp-post'),
        ('new-stamp-location-post', '/new-stamp-location-post'),
        ('sign-up-post', '/sign-up-post'),
    ):
        config.add_route(name, pattern, request_method='POST')


def add_static_views(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('static/images', 'Parks:images', cache_max_age=3600)
