from pyramid import testing

from parks.tests.test_base import UnitTestBase
from parks.views.new_stamp_location import new_stamp_location


class NewStampLocationUnitTest(UnitTestBase):
    # TODO(bskari|2013-02-02) Test the POST half of this form page.

    def test_view(self):
        request = testing.DummyRequest()
        page = new_stamp_location(request)

        # Post URL should be pointing here
        self.assertIn('post_url', page)
        self.assertEqual(page['post_url'], request.route_url('new-stamp-location-post'))
