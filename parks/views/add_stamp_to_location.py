# -*- coding: utf-8 -*-
import json
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
from pyramid.view import view_config
import re
from transaction import manager

from parks.logic import park as park_logic
from parks.logic import stamp as stamp_logic
from parks.logic import stamp_location as stamp_location_logic
from parks.logic import user as user_logic


@view_config(route_name='add-stamp-to-location', renderer='add_stamp_to_location.mako', permission='edit')
def add_stamp_to_location(request):
    render_dict = {}

    if 'form.submitted' in request.params:
        #park_name = request.params.get('park', None)
        #location = request.params.get('description', None)
        #address = request.params.get('address', None)
        #latitude = request.params.get('latitude', None)
        #longitude = request.params.get('longitude', None)
        #if park_name is None or description is None:
        #    render_dict.update(
        #        error='There was an error submitting that information.'
        #    )
        #else:
        #    try:
        #        park = park_logic.get_park_by_name(park_name)
        #        stamp_location_id = create_stamp_location(
        #            park_id=park.id,
        #            description=description,
        #            address=address,
        #            latitude=latitude,
        #            longitude=longitude,
        #            added_by_user=authenticated_userid(request)
        #        )
        #        return HTTPFound(
        #            location=request.route_url(
        #                'stamp-location',
        #                park=park.url,
        #                id=stamp_location_id,
        #            ),
        #        )
        #    except ValueError, e:
        #        render_dict.update(error=str(e))
        pass

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
    """Returns a JSON list of text of stamps that begin with the word in the
    'stamp_text' parameter.
    """
    partial_stamp = request.GET.get('stamp_text', None)
    if partial_stamp is None:
        return dict(success=False, error='No stamp text sent.')

    stamps = stamp_logic.get_stamps_beginning_with_string(partial_stamp)
    text_list = [s.text for s in stamps]

    return dict(success=True, stamps=text_list)
