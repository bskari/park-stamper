from mock import patch
from pyramid import testing

from parks.models import Park
from parks.models import StampLocation
from parks.tests.test_base import IntegrationTestBase
from parks.views.stamp_location import stamp_location


class StampLocationUnitTest(IntegrationTestBase):
    @patch('parks.logic.park.get_park_by_id')
    @patch('parks.logic.stamp_location.get_stamp_location_by_id')
    @patch('parks.logic.stamp.get_stamps_by_location_id')
    def test_view(
        self,
        mock_get_stamps_by_location_id,
        mock_get_stamp_location_by_id,
        mock_get_park_by_id,
    ):
        yellowstone_url = 'yellowstone'

        mock_get_park_by_id.return_value = Park(
            name='Yellowstone National Park',
            url=yellowstone_url,
            state=1,
            region='RM',
            type='NP',
        )
        mock_get_stamp_location_by_id.return_value = StampLocation(
            latitude=0,
            longitude=0,
            park_id=1,
        )

        request = testing.DummyRequest(referrer='')
        request.matchdict['id'] = '1'
        request.matchdict['park'] = yellowstone_url

        page = stamp_location(request)

        for mock_object in (
            mock_get_stamp_location_by_id,
            mock_get_park_by_id,
            mock_get_stamps_by_location_id,
        ):
            self.assertEqual(mock_object.call_count, 1)

        expected_keys = set(('stamps', 'stamp_location', 'park'))
        self.assertEqual(expected_keys, set(page.keys()))
