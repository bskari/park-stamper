from pyramid import renderers
from pyramid import testing
from transaction import manager
import random
import pyquery
import string
import types

from parks.logic.security import group_finder
from parks.logic.security import check_login_and_get_user_id
from parks.models import User
from parks.models import UserEmail
from parks.tests.test_base import IntegrationTestBase


class SecurityTestCase(IntegrationTestBase):
    def setUp(self):
        super(SecurityTestCase, self).setUp()

        self.username = 'guest'
        self.password = 'password'
        self.email = 'guest@example.com'
        self.user_id = None

    def _create_user(self):
        """Creates a user in the database."""
        with manager:
            user = User(
                username=self.username,
                password=self.password,
                signup_ip=1,
            )
            self.session.add(user)
            self.user_id = self.session.query(User.id).first().id
            user_email = UserEmail(
                user=self.user_id,
                email=self.email,
            )
            self.session.add(user_email)

    def _delete_user(self):
        """Deletes a user in the database."""
        with manager:
            self.session.query(
                User
            ).filter(
                User.id == self.user_id
            ).delete()

            self.session.query(
                UserEmail
            ).filter(
                UserEmail.email == self.email
            ).delete()

    def test_group_finder(self):
        """Tests the security group finder."""
        self._create_user()
        request = testing.DummyRequest()
        # Right now, group finder just returns the 'user' group if a user is
        # logged in
        group = group_finder(self.user_id, request)
        self.assertEqual(['group:users'], group)

        group = group_finder(None, request)
        self.assertIs(group, None)

        self._delete_user()

    def test_check_login_and_get_user_id(self):
        """Tests checking the login user and password."""
        self._create_user()
        # Email and username should both work for logging in
        user_id = check_login_and_get_user_id(self.email, self.password)
        self.assertEqual(self.user_id, user_id)
        user_id = check_login_and_get_user_id(self.username, self.password)
        self.assertEqual(self.user_id, user_id)

        # Failed logins
        user_id = check_login_and_get_user_id(self.email, 'bad password')
        self.assertIs(user_id, None)
        user_id = check_login_and_get_user_id(self.username, 'bad password')
        self.assertEqual(user_id, None)
        user_id = check_login_and_get_user_id('notexist', self.password)
        self.assertIs(user_id, None)
        user_id = check_login_and_get_user_id('not@exist.com', self.password)
        self.assertEqual(user_id, None)
        user_id = check_login_and_get_user_id('not@exist.com', 'bad password')
        self.assertEqual(user_id, None)

        self._delete_user()

    def test_csrf_in_forms(self):
        """Tests that CSRF is loaded into all forms on a page."""
        # We're doing this in two steps: first, all requests should csrf token
        # insterted into the render dict; and second, the base mako template
        # should try to add it to all forms
        namespaced_type = types.SimpleNamespace(name='')
        request = testing.DummyRequest(matched_route=namespaced_type)
        csrf_token = ''.join((
            random.choice(string.ascii_letters) for _ in range(10)
        ))
        parameters = {
            'post_url': 'log-in-post',
            'login': 'test_user',
            'csrf_token': csrf_token,
        }
        response = renderers.render('log_in.mako', parameters, request)

        html = pyquery.PyQuery(response)

        # Make sure that the CSRF token is in the page
        csrf_token_id = 'csrf-token'
        hidden_inputs = html('input[type=hidden]#' + csrf_token_id)
        self.assertEqual(len(hidden_inputs), 1)
        self.assertIn('value', hidden_inputs[0].attrib)
        self.assertEqual(csrf_token, hidden_inputs[0].attrib['value'])

        # Make sure that there is a script to add the CSRF to each form
        scripts = [
            s for s in html('script') if s.text is not None and 'csrf' in s.text
        ]
        self.assertEqual(len(scripts), 1)
        csrf_script = scripts[0]
        self.assertIn("$('#" + csrf_token_id + "')", csrf_script.text)
        self.assertIn("$('form').add(", csrf_script.text)
