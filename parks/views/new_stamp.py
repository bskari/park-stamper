from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
import transaction

from parks.logic import stamp


@view_config(route_name='new-stamp', renderer='new_stamp.mako')
def new_stamp(request):
    render_dict = {}

    if 'form.submitted' in request.params:
        # Use a fake loop so that I can bail out early on errors
        for _ in xrange(1):
            location_id = request.params.get('location', None)
            text = request.params.get('text', None)

            if stamp.stamp_exists(text):
                render_dict.update(
                    #TODO(bskari|2013-01-06) Make this click here go somewhere
                    error="I already have a stamp with that text. Did you find that stamp at another location? If so, click here to add it to that location."
                )
                break

            try:
                stamp_id = stamp.create_new_stamp(text)
                stamp_location.add_stamp_to_location(stamp_id, location_id)
            except:
                render_dict.update(
                    error="Whoops, something broke on my end. Please try again later.",
                )
                break

            location = stamp_location.get_stamp_location_by_id(location_id)
            return HTTPFound(
                location=request.route_url('park', park_url=location.park.url)
            )


    new_stamp_url = request.route_url('new-stamp')
    render_dict.update(
        url=new_stamp_url,
    )

    return render_dict
