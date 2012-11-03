from pyramid import testing
from sqlalchemy import create_engine
from unittest import TestCase
from transaction import manager

from .models import DBSession
from .models import Base
from .models import User
from .views import main

class TestMainView(TestCase):
    def setUp(self):
        self.config = testing.setUp()
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with manager:
            model = User(username='guest', password='password', signup_ip=1)
            DBSession.add(model)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_it(self):
        request = testing.DummyRequest()
        info = main(request)
        #self.assertEqual(info['one'].name, 'one')
        #self.assertEqual(info['project'], 'Parks')
