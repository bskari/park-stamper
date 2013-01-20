from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from parks.logic.park import get_park_and_state_by_url
from parks.logic.stamp import get_stamps_by_park_id


@view_config(route_name='park', renderer='park.mako')
def park(request):
    park_url = request.matchdict['park_url']
    park_state = get_park_and_state_by_url(park_url)

    if len(park_state) == 0:
        return HTTPNotFound('No park found')
    if len(park_state) != 1:
        return HTTPNotFound('Internal error: multiple parks found')
    park, state = park_state[0]

    stamps = get_stamps_by_park_id(park.id)

    render_context = dict()

    # When a new stamp is created, we POST to a certain URL and then return
    # HTTPFound to direct the user here. There's no way that I've figured out
    # to set the message from there, so just do it here.
    if request.referrer == request.route_url('new-stamp'):
        render_context.update(
            success='Great! Thanks for the update! Here are the other stamps'
                ' from that park.'
        )

    render_context.update(park=park, state=state, stamps=stamps)
    return render_context
