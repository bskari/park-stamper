import os
import sys
import transaction

from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging
from sqlalchemy import engine_from_config

from ..models import DBSession
from ..models import Base

from ..models import Park
from ..models import Stamp
from ..models import StampCollection
from ..models import State
from ..models import User
from ..models import UserEmail


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd)) 
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    # Create test data
    with transaction.manager:
        user = User(username='guest', password='password', signup_ip=1)
        DBSession.add(user)
        user = DBSession.query(User.id).filter(User.username == 'guest').first()
        user_email = UserEmail(user=user.id, email='guest@parkstamper.org')
        DBSession.add(user_email)
        for name, abbreviation in (
            ('Colorado', 'co'),
            ('New York', 'ny'),
            ('Utah', 'ut'),
            ('Virginia', 'va'),
            ('Wyoming', 'wy'),
        ):
            state = State(name=name, abbreviation=abbreviation, type='state')
            DBSession.add(state)
        park_info = (
            ('Arches', 'arches', 'ut'),
            ('Grand Tetons', 'grand-tetons', 'wy'),
            ('Great Sand Dunes', 'great-sand-dunes', 'co'),
            ('Shenandoah', 'shenandoah', 'va'),
            ('Statue of Liberty', 'statue-of-liberty', 'ny'),
            ('Yellowstone', 'yellowstone', 'wy'),
        )
        for name, url, state in park_info:
            park = Park(name=name, url=url, state=state)
            DBSession.add(park)
        for name, _, _ in park_info:
            stamp = Stamp(park=name, text=(name + '\nNational Park'))
            DBSession.add(stamp)
            # Uses can collect stamps more than once
            for i in xrange(2):
                collection = StampCollection(user.id, stamp.id)
                DBSession.add(collection)
