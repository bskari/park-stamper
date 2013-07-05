from pyramid import testing
from sqlalchemy import create_engine
from unittest import TestCase

from parks.models import DBSession
from parks.models import Base
from parks.routes import add_routes
from parks.routes import add_static_views


class UnitTestBase(TestCase):
    def setUp(self):
        self.config = testing.setUp()
        add_routes(self.config)
        add_static_views(self.config)

    def tearDown(self):
        testing.tearDown()


class IntegrationTestBase(UnitTestBase):
    def setUp(self):
        super(IntegrationTestBase, self).setUp()
        engine = create_engine('sqlite://')
        self.session = DBSession
        self.session.configure(bind=engine)
        Base.metadata.create_all(engine)

    def tearDown(self):
        DBSession.remove()
        super(IntegrationTestBase, self).tearDown()
