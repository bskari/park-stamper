from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from parks.logic import park as park_logic
from parks.logic import stamp as stamp_logic
from parks.logic import stamp_location as stamp_location_logic


@view_config(route_name='park', renderer='park.mako')
def park(request):
    park_url = request.matchdict['park_url']
    park_state = park_logic.get_park_and_state_by_url(park_url)

    if len(park_state) == 0:
        return HTTPNotFound('No park found')
    if len(park_state) != 1:
        return HTTPNotFound('Internal error: multiple parks found')
    park, state = park_state[0]

    stamps = stamp_logic.get_stamps_by_park_id(park.id)
    stamp_locations = stamp_location_logic.get_stamp_locations_by_park_id(park.id)

    render_context = dict()

    # When a new stamp is created, we POST to a certain URL and then return
    # HTTPFound to direct the user here. There's no way that I've figured out
    # to set the message from there, so just do it here.
    if request.referrer == request.route_url('new-stamp'):
        render_context.update(
            success='Great! Thanks for the update! Here are the other stamps'
                ' from that park.'
        )
    elif request.referrer == request.route_url('new-stamp-location'):
        # TODO(bskari|2013-01-26) Make this link go somewhere
        render_context.update(
            success='Nice! Would you like to add some stamps to that location?'
        )

    render_context.update(
        park=park,
        state=state,
        stamps=stamps,
        stamp_locations=stamp_locations,
    )
    return render_context
