import datetime
import os
import sys
import transaction

from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging
from sqlalchemy import engine_from_config

from parks.models import DBSession
from parks.models import Base
from parks.models import Park
from parks.models import Stamp
from parks.models import StampCollection
from parks.models import State
from parks.models import User
from parks.models import UserEmail


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
        user_id = DBSession.query(User.id).filter(User.username == 'guest').scalar()
        user_email = UserEmail(user=user_id, email='guest@parkstamper.org')
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
            stamp_text = name + '\nNational Park'
            for text in (stamp_text, stamp_text.upper(), stamp_text.lower()):
                stamp = Stamp(park=name, text=text)
                DBSession.add(stamp)

                # Let's leave some stamps uncollected
                if text != stamp_text.lower():
                    stamp_id = DBSession.query(
                        Stamp.id
                    ).filter(
                        Stamp.text == text
                    ).scalar()
                    # Users can collect stamps more than once
                    for i in xrange(2):
                        collection = StampCollection(
                            stamp_id=stamp_id,
                            user_id=user_id,
                            time_collected=datetime.datetime.now() - datetime.timedelta(days=i),
                        )
                        DBSession.add(collection)
