from pyramid import testing

from parks.tests.integration_test_base import IntegrationTestBase
from parks.views.main import main


class MainUnitTest(IntegrationTestBase):
    def test_view(self):
        request = testing.DummyRequest()
        page = main(request)

        self.assertIn('carousel_information', page.keys())
        self.assertGreaterEqual(len(page['carousel_information']), 2)
