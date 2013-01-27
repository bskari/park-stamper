from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
import json
from transaction import manager

from parks.logic import park as park_logic
from parks.logic import stamp_location as stamp_location_logic


@view_config(route_name='new-stamp-location', renderer='new_stamp_location.mako')
def new_stamp_location(request):
    render_dict = {}

    if 'form.submitted' in request.params:
        park_name = request.params.get('park', None)
        description = request.params.get('description', None)
        address = request.params.get('address', None)
        latitude = request.params.get('latitude', None)
        longitude = request.params.get('longitude', None)
        if park_name is None or description is None:
            render_dict.update(
                error='There was an error submitting that information.'
            )
        else:
            try:
                park = park_logic.get_park_by_name(park_name)
                stamp_location_id = create_stamp_location(
                    park_id=park.id,
                    description=description,
                    address=address,
                    latitude=latitude,
                    longitude=longitude,
                )
                return HTTPFound(
                    location=request.route_url(
                        'stamp-location',
                        park=park.url,
                        id=stamp_location_id,
                    ),
                )
            except ValueError, e:
                render_dict.update(error=str(e))

    new_stamp_location_url = request.route_url('new-stamp-location')
    parks = park_logic.get_all_park_names()
    parks_json_string = json.dumps(parks).replace("'", "\\'")
    render_dict.update(
        url=new_stamp_location_url,
        parks_json_string=parks_json_string,
    )

    return render_dict


def create_stamp_location(park_id, description, address, latitude, longitude):
    """Creates a new stamp location at the park."""
    with manager:
        if stamp_location_logic.stamp_location_exists(park_id, description):
            #TODO(bskari|2013-01-24) Make this click here go somewhere
            raise ValueError(
                "There's already a location with that description. Would you"
                " like to see all of the stamp locations at that park?"
            )

        address, latitude, longitude = [
            None if s == '' else s
            for s in address, latitude, longitude
        ]

        id_ = stamp_location_logic.create_new_stamp_location(
            park_id=park_id,
            description=description,
            address=address,
            latitude=latitude,
            longitude=longitude,
        )
        return id_
