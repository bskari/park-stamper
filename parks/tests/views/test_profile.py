from mock import patch
from pyramid import testing

import parks.logic.park
from parks.models import User
from parks.tests.integration_test_base import IntegrationTestBase
from parks.views.profile import profile_user


class ProfileUnitTest(IntegrationTestBase):
    @patch.object(parks.logic.user, 'get_user_by_username_or_email')
    def test_profile_user_view(self, mock_get_user_by_username_or_email):
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
        pass
