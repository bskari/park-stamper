from pyramid.security import authenticated_userid
from pyramid.view import view_config

from parks.logic import stamp as stamp_logic
from parks.models import DBSession
from parks.models import Stamp


default_values = {
    'type_values': Stamp.type.property.columns[0].type.enums,
    'status_values': Stamp.status.property.columns[0].type.enums,
}


@view_config(route_name='edit-stamp', renderer='edit_stamp.mako', permission='edit')
def edit_stamp(request):
    stamp_id = int(request.matchdict['id'])
    stamp = DBSession.query(
        Stamp
    ).filter(
        Stamp.id == stamp_id
    ).one()

    render_dict = {}
    render_dict.update(default_values)
    render_dict.update({
        'stamp': stamp,
        'post_url': request.route_url('edit-stamp-post', id=stamp_id),
    })
    return render_dict


@view_config(route_name='edit-stamp-post', renderer='edit_stamp.mako', permission='edit')
def edit_stamp_post(request):
    if 'form.submitted' not in request.params:
        # How did we get to a POST endpoint without a form?
        return {
            'error': 'Sorry, there was an error submitting that information.'
        }

    stamp_id = request.params.get('stamp-id', None)
    text = request.params.get('text', None)
    type = request.params.get('type', None)
    status = request.params.get('status', None)

    if stamp_id is None or text is None or type is None or status is None:
        return {
            'error': 'There was an error submitting that information.'
        }
    else:
        try:
            stamp_id = int(stamp_id)
            stamp_logic.edit_stamp(
                stamp_id,
                text,
                type,
                status,
                authenticated_userid(request)
            )

            stamp = DBSession.query(
                Stamp
            ).filter(
                Stamp.id == stamp_id
            ).one()

            render_dict = {}
            render_dict.update(default_values)
            render_dict.update({
                'stamp': stamp,
                'post_url': request.route_url('edit-stamp-post', id=stamp.id),
                'success': 'Stamp updated!',
            })
            return render_dict

        except ValueError as e:
            return {'error': str(e)}
