# -*- coding: utf-8 -*-
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from parks.logic import park as park_logic
from parks.logic import stamp as stamp_logic
from parks.logic import stamp_location as stamp_location_logic


@view_config(route_name='add-stamp-to-location', renderer='add_stamp_to_location.mako', permission='edit')
def add_stamp_to_location(request):
    render_dict = {}


    url = request.route_url('add-stamp-to-location-post')
    # We may have been redirected here after being primpted to add some stamps
    # to a location that had none
    stamp_location_id = request.GET.get('stamp-location-id', None)
    if stamp_location_id is not None:
        try:
            stamp_location = stamp_location_logic.get_stamp_location_by_id(
                stamp_location_id
            )
            park = park_logic.get_park_by_id(stamp_location.park_id)
            park_name = park.name
        except:
            stamp_location_id = None
            park_name = None
    else:
        park_name = None

    render_dict.update(
        add_stamp_to_location_post_url=url,
        stamp_locations_url=request.route_url('stamp-locations-json'),
        stamps_url=request.route_url('stamps-substring-json'),
        stamp_location_id=stamp_location_id,
        park_name = park_name,
    )

    return render_dict


@view_config(route_name='add-stamp-to-location-post', renderer='add_stamp_to_location.mako', permission='edit')
def add_stamp_to_location_post(request):
    if 'add-stamp-to-location' in request.params:
        stamp_location_id = request.params.get('location', None)
        stamp_ids = request.params.getall('stamp')

        if stamp_location_id is None:
            render_dict.update(
                error='There was an error submitting that information.'
            )
        elif len(stamp_ids) == 0:
            render_dict.update(
                error='Please select some stamps.'
            )
        else:
            try:
                stamp_location_id = int(stamp_location_id)
                for stamp_id in stamp_ids:
                    stamp_id = int(stamp_id)
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
            except ValueError as e:
                render_dict.update(error=str(e))


@view_config(route_name='stamps-substring-json', renderer='json')
def stamps_json(request):
    """Returns a JSON list of stamps that begin with the word in the
    'stampText' parameter. The returned JSON includes the stamp's text and
    the stamp's ID. Example:
    [{text: "Yellowstone NP Visitor Center", id: 83}]
    """
    partial_stamp = request.GET.get('stampText', None)
    if partial_stamp is None:
        return dict(success=False, error='No stamp text sent.')

    stamps = stamp_logic.get_stamps_beginning_with_string(partial_stamp)
    stamps = [dict(text=s.text, id=s.id) for s in stamps]

    return dict(success=True, stamps=stamps)
