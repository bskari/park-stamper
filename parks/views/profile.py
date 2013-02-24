from pyramid.security import authenticated_userid
from pyramid.view import view_config

from parks.logic import stamp_collection as stamp_collection_logic
from parks.logic import user as user_logic
from parks.logic import user_email as user_email_logic


@view_config(route_name='profile-user', renderer='profile.mako')
def profile_user(request, username=None):
    render_context = dict(personal_profile=False)

    if username is None:
        username = request.matchdict['username']
        render_context.update(username=username)
    user_id = authenticated_userid(request)
    if user_id is not None:
        user = user_logic.get_user_by_id(user_id)
        # If a user is accessing their own profile, then show them everything
        if user.username == username:
            return profile_personal(request)
    else:
        user = user_logic.get_user_by_username_or_email(username)
        user_id = user.id

    render_context.update(_profile_common(request, user_id))

    return render_context


@view_config(
    route_name='profile-personal',
    renderer='profile.mako',
    permission='logged-in',
)
def profile_personal(request):
    render_context = dict(personal_profile=True)
    user_id = authenticated_userid(request)
    user = user_logic.get_user_by_id(user_id)
    user_emails = user_email_logic.get_emails_by_user_id(user_id)
    render_context.update(user=user, user_emails=user_emails)

    render_context.update(_profile_common(request, user_id))

    return render_context


def _profile_common(request, user_id):
    render_context = {}

    days = 30
    stamp_collections = stamp_collection_logic.get_recent_collections_by_user_id(
        user_id,
        days
    )
    render_context.update(days=days, stamp_collections=stamp_collections)

    return render_context
