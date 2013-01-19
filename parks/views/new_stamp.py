from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
import json
import transaction

from parks.logic import park
from parks.logic import stamp


@view_config(route_name='new-stamp', renderer='new_stamp.mako')
def new_stamp(request):
    render_dict = {}

    if 'form.submitted' in request.params:
        try:
            response = save_stamp(
                request.params.get('location', None),
                request.params.get('text', None),
            )
            return response
        except Exception, e:
            render_dict.update(str(e))

    new_stamp_url = request.route_url('new-stamp')
    parks = park.get_all_park_names()
    parks_json_string = json.dumps(parks).replace("'", "\\'")
    render_dict.update(
        url=new_stamp_url,
        parks_json_string=parks_json_string,
    )

    return render_dict


def save_stamp(location, text):
    if stamp.stamp_exists(text):
        #TODO(bskari|2013-01-06) Make this click here go somewhere
        raise Exception(
            "I already have a stamp with that text. Did you find that stamp at"
            " another location? If so, click here to add it to that location."
        )

    try:
        stamp_id = stamp.create_new_stamp(text)
        stamp_location.add_stamp_to_location(stamp_id, location_id)
    except:
        raise Exception(
            "Whoops, something broke on my end. Please try again later."
        )

    location = stamp_location.get_stamp_location_by_id(location_id)
    return HTTPFound(
        location=request.route_url('park', park_url=location.park.url)
    )
