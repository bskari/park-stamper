from collections import namedtuple
from mock import patch
from pyramid import testing

from parks.models import State
from parks.models import Park
from parks.tests.test_base import IntegrationTestBase
from parks.views.park import park


class ParkUnitTest(IntegrationTestBase):
    @patch('parks.logic.park.get_park_and_state_by_url')
    def test_view(self, mock_get_park_and_state_by_url):
        yellowstone_url = 'yellowstone'

        ParkStateMockTuple = namedtuple(
            'ParkStateMockTuple',
            ['Park', 'State']
        )
        fake_park = Park(
            name='Yellowstone National Park',
            url=yellowstone_url,
            state=1,
            region='RM',
            type='NP',
        )
        fake_park_and_state_list = (
            ParkStateMockTuple(
                fake_park,
                State(
                    name='Wyoming',
                    abbreviation='WY',
                    type='state',
                )
            ),
        )

        mock_get_park_and_state_by_url.return_value = fake_park_and_state_list

        request = testing.DummyRequest(referrer='')
        request.matchdict['park_url'] = yellowstone_url

        page = park(request)

        self.assertEqual(mock_get_park_and_state_by_url.call_count, 1)

        expected_keys = set(('stamps', 'stamp_locations', 'park', 'state'))
        self.assertEqual(expected_keys, set(page.keys()))
        self.assertEqual(fake_park, page['park'])
