from pyramid import testing

from parks.tests.test_base import IntegrationTestBase
from parks.views.add_stamp_to_location import add_stamp_to_location


class AddStampToLocationUnitTest(IntegrationTestBase):
    # TODO(bskari|2014-10-06) Test the POST half of this form page.

    def test_urls(self):
        """Test that the urls are correct."""
        request = testing.DummyRequest()
        page = add_stamp_to_location(request)
        self.assertIn('post_url', page)
        self.assertEqual(
            page['post_url'],
            request.route_url('add-stamp-to-location-post')
        )
