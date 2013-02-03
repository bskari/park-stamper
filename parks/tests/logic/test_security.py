from pyramid import testing
from transaction import manager

from parks.logic.security import group_finder
from parks.logic.security import check_login_and_get_username
from parks.models import User
from parks.models import UserEmail
from parks.tests.integration_test_base import IntegrationTestBase


class SecurityTestCase(IntegrationTestBase):
    def setUp(self):
        super(SecurityTestCase, self).setUp()

        self.username = 'guest'
        self.password = 'password'
        self.email = 'guest@example.com'

    def _create_user(self):
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
        self._create_user()
        request = testing.DummyRequest()
        # Right now, group finder just returns the 'user' group if a user is
        # logged in
        group = group_finder(self.user_id, request)
        self.assertEqual(['group:users'], group)

        group = group_finder(None, request)
        self.assertIs(group, None)

        self._delete_user()

    def test_check_login_and_get_username(self):
        self._create_user()
        # Email and username should both work for logging in
        username = check_login_and_get_username(self.email, self.password)
        self.assertEqual(self.username, username)
        username = check_login_and_get_username(self.username, self.password)
        self.assertEqual(self.username, username)

        # Failed logins
        username = check_login_and_get_username(self.email, 'bad password')
        self.assertIs(username, None)
        username = check_login_and_get_username(self.username, 'bad password')
        self.assertEqual(username, None)

        self._delete_user()
