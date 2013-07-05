from mock import patch
from pyramid import testing

from parks.models import User
from parks.tests.test_base import UnitTestBase
from parks.views.profile import profile_user


class ProfileUnitTest(UnitTestBase):
    @patch('parks.logic.user.get_user_by_username_or_email')
    @patch('parks.logic.stamp_collection.get_recent_collections_by_user_id')
    def test_profile_user_view(self, mock_get_user_by_username_or_email, _):
        mock_get_user_by_username_or_email.return_value = User(
            username='guest',
            password='123',
            signup_ip=1,
        )

        request = testing.DummyRequest()
        request.matchdict['username'] = 'guest'

        page = profile_user(request)

        expected_keys = set((
            'stamp_collections',
            'days',
            'personal_profile',
            'username',
        ))
        self.assertEqual(expected_keys, set(page.keys()))

    def test_profile_personal_view(self):
        # TODO (bskari|2013-07-04) Implement this
        pass
