from mock import patch
from pyramid import testing

from parks.tests.test_base import IntegrationTestBase
from parks.views.home import home


class HomeUnitTest(IntegrationTestBase):
    @patch('parks.logic.user.get_recent_user_collections')
    def test_view(self, mock_get_recent_user_collections):
        request = testing.DummyRequest()
        page = home(request)

        self.assertEqual(mock_get_recent_user_collections.call_count, 1)

        self.assertIn('carousel_information', page)
        self.assertGreaterEqual(len(page['carousel_information']), 2)
