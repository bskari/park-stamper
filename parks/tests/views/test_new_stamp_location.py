from pyramid import testing

from parks.tests.integration_test_base import IntegrationTestBase
from parks.views.new_stamp_location import new_stamp_location


class NewStampLocationUnitTest(IntegrationTestBase):
    # TODO(bskari|2013-02-02) Test the POST half of this form page.

    def test_view(self):
        request = testing.DummyRequest()
        page = new_stamp_location(request)

        # Post URL should be pointing here
        self.assertIn('post_url', page)
        self.assertEqual(page['post_url'], request.route_url('new-stamp-location-post'))
