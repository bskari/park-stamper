from mock import patch
from pyramid import testing

from parks.models import Park
from parks.tests.test_base import IntegrationTestBase
from parks.views.all_parks import all_parks


class AllParksUnitTest(IntegrationTestBase):
    @patch('parks.logic.park.get_all_parks')
    def test_view(self, mock_get_all_parks):
        request = testing.DummyRequest()

        test_parks = (
            Park(
                name='test',
                url='www.nps.gov/test_park',
                state=1,
                region='NA',
                type='NP',
            ),
        )

        mock_get_all_parks.return_value = test_parks

        page = all_parks(request)

        self.assertEqual(mock_get_all_parks.call_count, 1)

        self.assertIn('parks', page)
        self.assertEqual(page['parks'], test_parks)
