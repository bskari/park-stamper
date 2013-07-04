from pyramid import testing

from parks.tests.integration_test_base import IntegrationTestBase
from parks.views.home import home


class HomeUnitTest(IntegrationTestBase):
    def test_view(self):
        request = testing.DummyRequest()
        page = home(request)

        self.assertIn('carousel_information', page)
        self.assertGreaterEqual(len(page['carousel_information']), 2)
