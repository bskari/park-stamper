# -*- coding: utf-8 -*-
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config


@view_config(route_name='collect-stamp', renderer='json', permission='edit')
def collect_stamp(request):
    if request.method != 'POST' or 'form.submitted' not in request.params:
        raise HTTPNotFound('POST required for collecting stamps')

    stamp_id = request.params.post('stamp', None)
    date = request.params.post('date', None)
    if stamp_id is None or date is None:
        raise HTTPNotFound('Stamp not provided')

    try:
        stamp_id = int(stamp_id)
        return dict(success=True)
    except ValueError:
        return dict(success=False)
