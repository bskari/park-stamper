import datetime
from pyramid.security import authenticated_userid
from pyramid.view import view_config

from parks.logic import stamp_collection as stamp_collection_logic


# Don't decorate this with permission='edit' because otherwise it will try to
# redirect users to a log in page and the JS will get confused
@view_config(route_name='collect-stamp', renderer='json')
def collect_stamp(request):
    if request.method != 'POST':
        return {'success': False}

    render_dict = {}

    stamp_id = request.params.get('stamp-id', None)
    park_id = request.params.get('park-id', None)
    date_string = request.params.get('date', None)
    if date_string is not None:
        try:
            # Date is formatted like: "2013-02-13"
            year = int(date_string[0:4])
            month = int(date_string[5:7])
            day = int(date_string[8:10])
            date = datetime.date(year=year, month=month, day=day)

            # Give some wiggle room for timezone concerns
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            if date > tomorrow:
                return {
                    'success': False,
                    'error': "You can't collect stamps in the future!",
                }
        except:
            date = None
    user_id = authenticated_userid(request)

    if stamp_id is None or park_id is None or date is None:
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
            stamp_collection_logic.collect_stamp(
                user_id=user_id,
                stamp_id=stamp_id,
                park_id=park_id,
                date=date
            )
        except ValueError, e:
            render_dict.update(success=False, error=str(e))
        else:
            render_dict.update(success=True)
            request.session['collect_date'] = date_string

    return render_dict
