from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound
from transaction import manager

from parks.logic import park as park_logic
from parks.logic import stamp as stamp_logic
from parks.logic import stamp_location as stamp_location_logic
from parks.logic import user as user_logic


@view_config(route_name='new-stamp', renderer='new_stamp.mako', permission='edit')
def new_stamp(request):
    render_dict = {}

    new_stamp_url = request.route_url('new-stamp-post')
    render_dict.update(
        post_url=new_stamp_url,
    )

    return render_dict


@view_config(route_name='new-stamp-post', renderer='new_stamp.mako', permission='edit')
def new_stamp_post(request):
    render_dict = {}
    if 'form.submitted' not in request.params:
        # How did we get to a POST endpoint without a form?
        render_dict.update(
            error='Sorry, there was an error submitting that information.'
        )
        return render_dict

    location_id = request.params.get('location', None)
    text = request.params.get('text', None)
    if location_id is None or text is None:
        render_dict.update(
            error='There was an error submitting that information.'
        )
    else:
        try:
            location_id = int(location_id)
            park_url = create_stamp(
                location_id,
                text,
                authenticated_userid(request)
            )
            return HTTPFound(
                location=request.route_url('park', park_url=park_url),
            )
        except ValueError, e:
            render_dict.update(error=str(e))


@view_config(route_name='stamp-locations-json', renderer='json')
def stamp_locations(request):
    park_name = request.GET.get('park', None)
    if park_name is None:
        return dict(success=False, error='No park provided.')

    try:
        park = park_logic.get_park_by_name(park_name)
    except NoResultFound:
        return dict(success=False, error='No park by that name found, please try again.')

    stamp_locations = stamp_location_logic.get_stamp_locations_by_park_id(park.id)
    location_and_id_list = [
        dict(
            location=sl.StampLocation.description or sl.StampLocation.address,
            id=sl.StampLocation.id
        )
        for sl in stamp_locations
    ]
    location_and_id_list.sort(key=lambda loc_and_id: loc_and_id['location'])

    return dict(
        success=True,
        stampLocations=location_and_id_list
    )


def create_stamp(location_id, text, user):
    """Creates a new stamp at the given location with the given text. On
    success, it returns the location's park's URL.
    """
    with manager:
        if stamp_logic.stamp_exists(text):
            #TODO(bskari|2013-01-06) Make this click here go somewhere
            raise ValueError(
                "I already have a stamp with that text. Did you find that stamp at"
                " another location? If so, click here to add it to that location."
            )

        if isinstance(user, str) or isinstance(user, unicode):
            user = user_logic.get_user_by_username_or_email(user).id

        stamp_id = stamp_logic.create_new_stamp(text, 'normal', user)
        stamp_location_logic.add_stamp_to_location(stamp_id, location_id)

        location = stamp_location_logic.get_stamp_location_by_id(location_id)
        park = park_logic.get_park_by_id(location.park_id)
        park_url = park.url

    return park_url
