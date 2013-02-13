from pyramid.security import authenticated_userid
from pyramid.view import view_config

#from parks.logic import stamp_collection as stamp_collection_logic


@view_config(route_name='collect-stamp', renderer='json', permission='edit')
def collect_stamp(request):
    if request.method != 'POST':
        return dict(success=False)

    render_dict = {}

    stamp_id = request.params.get('stampId', None)
    user_id = authenticated_userid(request)
    if stamp_id is None:
        render_dict.update(
            success=False,
            error='There was an error submitting that information.',
        )
    elif user_id is None:
        render_dict.update(
            success=False,
            error='You need to be logged in to collect stamps.',
        )
    else:
        try:
            pass
        except ValueError, e:
            render_dict.update(success=False, error=str(e))
        else:
            render_dict.update(success=True)

    return render_dict
