from mock import patch
from pyramid import testing

import parks.logic.park
import parks.logic.stamp
import parks.logic.stamp_location
from parks.models import Park
from parks.models import Stamp
from parks.models import StampLocation
from parks.tests.integration_test_base import IntegrationTestBase
from parks.views.stamp_location import stamp_location


class StampLocationUnitTest(IntegrationTestBase):
    @patch.object(parks.logic.park, 'get_park_by_id')
    @patch.object(parks.logic.stamp, 'get_stamps_by_park_id')
    @patch.object(parks.logic.stamp_location, 'get_stamp_location_by_id')
    def test_view(
        self,
        mock_get_stamp_location_by_id,
        mock_get_stamps_by_park_id,
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
        mock_get_stamps_by_park_id.return_vaue = [
            Stamp(
                text='some stamp text',
                type='normal',
                status='active',
            ),
        ]
        mock_get_stamp_location_by_id.return_value = StampLocation(
            latitude=0,
            longitude=0,
            park_id=1,
        )

        request = testing.DummyRequest(referrer='')
        request.matchdict['id'] = '1'

        page = stamp_location(request)
        expected_keys = set(('stamps', 'stamp_location', 'park'))
        self.assertEqual(expected_keys, set(page.keys()))
