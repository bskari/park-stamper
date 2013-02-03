from pyramid.httpexceptions import HTTPMovedPermanently
from pyramid.view import view_config
from parks.logic import park as park_logic
from parks.logic import stamp as stamp_logic
from parks.logic import stamp_location as stamp_location_logic


@view_config(route_name='stamp-location', renderer='stamp_location.mako')
def stamp_location(request):
    stamp_location_id = int(request.matchdict['id'])
    stamp_location = stamp_location_logic.get_stamp_location_by_id(stamp_location_id)
    park = park_logic.get_park_by_id(stamp_location.park_id)

    # The URL for this page looks like "stamp-location/{id}/{park}". The park
    # is ignored and is only for SEO, but if the park is wrong, we should
    # redirect the user to the correct URL so that people don't link to, e.g.,
    # "stamp-location/{id}/this-site-sucks".
    if request.matchdict['park'] != park.url:
        return HTTPMovedPermanently(
            location=request.route_url(
                'stamp-location',
                id=stamp_location_id,
                park=park.url
            )
        )

    stamps = stamp_logic.get_stamps_by_park_id(park.id)

    render_context = dict()

    # When a new stamp is created, we POST to a certain URL and then return
    # HTTPFound to direct the user here. There's no way that I've figured out
    # to set the message from there, so just do it here.
    if request.referrer == request.route_url('new-stamp-location'):
        # TODO(bskari|2013-01-26) Make this link go somewhere
        render_context.update(
            success='Nice! Would you like to add some stamps to that location?'
        )

    render_context.update(
        park=park,
        stamp_location=stamp_location,
        stamps=stamps,
    )
    return render_context
