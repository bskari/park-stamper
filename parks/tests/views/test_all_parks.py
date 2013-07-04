from pyramid import testing

from parks.tests.integration_test_base import IntegrationTestBase
from parks.views.all_parks import all_parks


class AllParksUnitTest(IntegrationTestBase):
    def test_view(self):
        request = testing.DummyRequest()
        page = all_parks(request)

        self.assertIn('parks', page)
        # TODO(bskari|2013-02-02) Create some park data
