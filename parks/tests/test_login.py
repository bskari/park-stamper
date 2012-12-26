from pyramid import testing
from pyramid.httpexceptions import HTTPFound
from transaction import manager

from parks.models import User
from parks.tests.integration_test_base import IntegrationTestBase
from parks.views.login import login

class LoginUnitTest(IntegrationTestBase):
    def setUp(self):
        super(LoginUnitTest, self).setUp()
        self.username = 'guest'
        self.password = 'password'
        with manager:
            model = User(
                username=self.username,
                password=self.password,
                signup_ip=1,
            )
            self.session.add(model)

    def test_came_from_is_never_login(self):
        """We should never be redirected back to the login page."""
        # Came from is set using the came_from parameter, or by the referrer
        # Check the came_from parameter
        request = testing.DummyRequest()
        login_url = request.route_url('login')
        request.params = dict(
            login=self.username,
            password=self.password,
            came_from=login_url,
        )
        page = login(request)
        self.assertIn('came_from', page.keys())
        self.assertNotEqual(page['came_from'], login_url)

        # Check the referrer URL
        request = testing.DummyRequest()
        request.params = dict(
            login=self.username,
            password=self.password,
        )
        request.referrer = login_url
        page = login(request)
        self.assertIn('came_from', page.keys())
        self.assertNotEqual(page['came_from'], login_url)

    def test_came_from(self):
        """Login should redirect the user back to where they came from, using
        either the came_from parameter, or the referrer.
        """
        # Check the came_from parameter
        request = testing.DummyRequest()
        original_url = request.route_url('home')
        request.params = dict(
            login=self.username,
            password=self.password,
            came_from=original_url,
        )
        page = login(request)
        self.assertIn('came_from', page.keys())
        self.assertEqual(page['came_from'], original_url)

        # Check the referrer URL
        request = testing.DummyRequest()
        request.params = dict(
            login=self.username,
            password=self.password,
        )
        request.referrer = original_url
        page = login(request)
        self.assertIn('came_from', page.keys())
        # The trailing slash is getting stripped for some reason, so strip it
        # here when we check for it
        self.assertEqual(page['came_from'], original_url[:-1])

    def test_successful_login(self):
        request = testing.DummyRequest()
        original_url = request.route_url('home')
        request.params = {
            'login': self.username,
            'password': self.password,
            'came_from': original_url,
            'form.submitted': 'Log In',
        }
        response = login(request)
        self.assertIsInstance(response, HTTPFound)

    def test_failed_login(self):
        request = testing.DummyRequest()
        original_url = request.route_url('home')
        request.params = {
            'login': 'invalid user',
            'password': 'invalid password',
            'came_from': original_url,
            'form.submitted': 'Log In',
        }
        response = login(request)
        self.assertIn('error', response.keys())
