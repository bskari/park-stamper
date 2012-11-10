from pyramid import testing
from sqlalchemy import create_engine
from unittest import TestCase
from transaction import manager

from parks.models import DBSession
from parks.models import Base
from parks.models import User
from parks.routes import add_routes
from parks.routes import add_static_views
from parks.views.main import main

class MainViewTest(TestCase):
    def setUp(self):
        self.config = testing.setUp()
        add_routes(self.config)
        add_static_views(self.config)
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with manager:
            model = User(username='guest', password='password', signup_ip=1)
            DBSession.add(model)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_smoke(self):
        request = testing.DummyRequest()
        page = main(request)
        page # TODO(bskari|2012-05-12) Do something with the response
