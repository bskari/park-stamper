from collections import namedtuple
from mock import patch
from pyramid.testing import DummyRequest

import parks.logic.stamp
from parks.models import Park
from parks.models import Stamp
from parks.models import StampLocation
from parks.tests.integration_test_base import IntegrationTestBase
from parks.views.nearby import nearby_json


class NearbyUnitTest(IntegrationTestBase):
    def _test_direction(self, latitude, longitude, expected_direction):
        request = DummyRequest(
            params=dict(
                latitude=latitude,
                longitude=longitude
            )
        )
        json = nearby_json(request)
        self.assertIn('success', json.keys())
        self.assertEqual(json['success'], True)
        self.assertIn('stamps', json.keys())
        self.assertGreater(len(json['stamps']), 0)
        stamp = json['stamps'][0]
        self.assertIn('direction', stamp.keys())
        self.assertEqual(expected_direction, stamp['direction'])


    @patch.object(parks.logic.stamp, 'get_nearby_stamps')
    def test_nearby_json_directions(self, mock_get_nearby_stamps):
        NearbyStampMockTuple = namedtuple(
            'NearbyStampMock',
            ['StampLocation', 'Stamp', 'Park']
        )
        mock_get_nearby_stamps.return_value = [
            NearbyStampMockTuple(
                StampLocation(
                    latitude=0,
                    longitude=0,
                ),
                Stamp(
                    text='nearby json test stamp',
                    type='normal',
                    status='active',
                ),
                Park(
                    name='nearby json test park',
                    url='nearby json test park url',
                    state=1,
                    region='W',
                    type='NP',
                )
            )
        ]

        for latitude, longitude, direction in (
            (0.1, 0.1, 'southwest'),
            (-0.1, 0.1, 'northwest'),
            (-0.1, -0.1, 'northeast'),
            (0.1, -0.1, 'southeast'),
            (0, 0.1, 'west'),
            (0, -0.1, 'east'),
            (0.1, 0, 'south'),
            (-0.1, 0, 'north'),
        ):
            self._test_direction(latitude, longitude, direction)
