from collections import namedtuple
from mock import patch
from pyramid import testing

import parks.logic.park
from parks.models import State
from parks.models import Park
from parks.tests.integration_test_base import IntegrationTestBase
from parks.views.park import park


class ParkUnitTest(IntegrationTestBase):
    @patch.object(parks.logic.park, 'get_park_and_state_by_url')
    def test_view(self, mock_get_park_and_state_by_url):
        yellowstone_url = 'yellowstone'

        ParkStateMockTuple = namedtuple(
            'ParkStateMockTuple',
            ['Park', 'State']
        )
        mock_get_park_and_state_by_url.return_value = [
            ParkStateMockTuple(
                Park(
                    name='Yellowstone National Park',
                    url=yellowstone_url,
                    state=1,
                    region='RM',
                    type='NP',
                ),
                State(
                    name='Wyoming',
                    abbreviation='WY',
                    type='state',
                )
            ),
        ]

        request = testing.DummyRequest(referrer='')
        request.matchdict['park_url'] = 'yellowstone'

        page = park(request)

        expected_keys = set(('stamps', 'stamp_locations', 'park', 'state'))
        self.assertEqual(expected_keys, set(page.keys()))
