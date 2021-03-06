from pyramid import testing

from parks.tests.test_base import IntegrationTestBase
from parks.views.new_stamp import new_stamp


class NewStampUnitTest(IntegrationTestBase):
    # TODO(bskari|2013-02-02) Test the POST half of this form page.

    def test_urls(self):
        """Test that the urls are correct."""
        request = testing.DummyRequest()
        page = new_stamp(request)
        self.assertIn('post_url', page)
        self.assertTrue(page['post_url'], 'post')
        self.assertEqual(
            page['post_url'],
            request.route_url('new-stamp-post')
        )
