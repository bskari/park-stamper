# -*- coding: utf-8 -*-
import json
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from parks.logic import park as park_logic
from parks.logic import stamp as stamp_logic
from parks.logic import stamp_location as stamp_location_logic


@view_config(route_name='add-stamp-to-location', renderer='add_stamp_to_location.mako', permission='edit')
def add_stamp_to_location(request):
    render_dict = {}

    if 'form.submitted' in request.params:
        stamp_location_id = request.params.get('location', None)
        stamp_id = request.params.get('stamp', None)
        if stamp_location_id is None or stamp_id is None:
            render_dict.update(
                error='There was an error submitting that information.'
            )
        else:

            try:
                stamp_location_id = int(stamp_location_id)
                stamp_location_logic.add_stamp_to_location(
                    stamp_id,
                    stamp_location_id
                )
                stamp_location = stamp_location_logic.get_stamp_location_by_id(
                    stamp_location_id
                )
                park = park_logic.get_park_by_id(stamp_location.park_id)
                return HTTPFound(
                    location=request.route_url('park', park_url=park.url),
                )
            except ValueError, e:
                render_dict.update(error=str(e))

    url = request.route_url('add-stamp-to-location')
    parks = park_logic.get_all_park_names()
    parks_json_string = json.dumps(parks).replace("'", "\\'")
    render_dict.update(
        add_stamp_to_location_post_url=url,
        parks_json_string=parks_json_string,
        stamp_locations_url=request.route_url('stamp-locations-json'),
        stamps_url=request.route_url('stamps-substring-json'),
    )

    return render_dict


@view_config(route_name='stamps-substring-json', renderer='json')
def stamps_json(request):
    """Returns a JSON list of stamps that begin with the word in the
    'stamp_text' parameter. The returned JSON includes the stamp's text and
    the stamp's ID. Example:
    [{text: "Yellowstone NP Visitor Center", id: 83}]
    """
    partial_stamp = request.GET.get('stamp_text', None)
    if partial_stamp is None:
        return dict(success=False, error='No stamp text sent.')

    stamps = stamp_logic.get_stamps_beginning_with_string(partial_stamp)
    stamps = [dict(text=s.text, id=s.id) for s in stamps]

    return dict(success=True, stamps=stamps)
