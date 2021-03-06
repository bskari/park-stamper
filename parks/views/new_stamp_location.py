# -*- coding: utf-8 -*-
"""Functions for creating a new stamp location."""
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
from pyramid.view import view_config
from transaction import manager
import re

from parks.logic import park as park_logic
from parks.logic import stamp_location as stamp_location_logic
from parks.logic import user as user_logic


@view_config(
    route_name='new-stamp-location',
    renderer='new_stamp_location.mako',
    permission='edit'
)
def new_stamp_location(request):
    """Handles the create a new stamp page."""
    render_dict = {}

    new_stamp_location_url = request.route_url('new-stamp-location-post')
    render_dict.update(
        post_url=new_stamp_location_url,
    )

    return render_dict


@view_config(
    route_name='new-stamp-location-post',
    renderer='new_stamp_location.mako',
    permission='edit'
)
def new_stamp_location_post(request):
    """Handles the POST endpoint of making a new stamp location."""
    new_stamp_location_url = request.route_url('new-stamp-location-post')
    render_dict = {
        'post_url': new_stamp_location_url,
    }

    if len(request.params) == 0:
        # How did we get to a POST endpoint without a form?
        new_stamp_location_url = request.route_url('new-stamp-location-post')
        render_dict.update(
            error='Sorry, there was an error submitting that information.',
        )
        return render_dict

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
                added_by_user=authenticated_userid(request),
            )
            return HTTPFound(
                location=request.route_url(
                    'stamp-location',
                    park=park.url,
                    id=stamp_location_id,
                ),
            )
        except ValueError as error:
            render_dict.update(error=str(error))

    return render_dict


def create_stamp_location(
    park_id,
    description,
    address,
    latitude,
    longitude,
    added_by_user,
):
    """Creates a new stamp location at the park."""
    with manager:
        if stamp_location_logic.stamp_location_exists(park_id, description):
            #TODO(bskari|2013-01-24) Make this click here go somewhere
            raise ValueError(
                "There's already a location with that description. Would you"
                " like to see all of the stamp locations at that park?"
            )

        address, latitude, longitude = (
            None if s == '' else s
            for s in (address, latitude, longitude)
        )

        # Basic validation
        if latitude is not None:
            # Remove non-numerical stuff from strings like '34.5° N'
            latitude = re.sub(r'[^\d\.-]', '', latitude)
            latitude = float(latitude)
            if latitude > 90.0 or latitude < -90.0:
                raise ValueError('Latitude needs to be between -90 and 90.')
        if longitude is not None:
            # Remove non-numerical stuff from strings like '80.4° W'
            longitude = re.sub(r'[^\d\.-]', '', longitude)
            longitude = float(longitude)
            if longitude > 0.0:
                # So, GPS devices will show 120.54 W instead of negative
                # values, so let's just negate it
                longitude = -longitude
            if longitude < -180.0:
                raise ValueError('Longitude needs to be between -180 and 180.')

        if isinstance(added_by_user, str) or isinstance(added_by_user, bytes):
            added_by_user = user_logic.get_user_by_username_or_email(
                added_by_user
            ).id

        id_ = stamp_location_logic.create_new_stamp_location(
            park_id=park_id,
            description=description,
            address=address,
            latitude=latitude,
            longitude=longitude,
            added_by_user_id=added_by_user,
        )
        return id_
