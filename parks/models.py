from datetime import datetime
from bcrypt import gensalt
from bcrypt import hashpw
from socket import inet_aton
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Date
from sqlalchemy import Time
from sqlalchemy import Enum
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import or_
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class User(Base):
    """A user on the site."""
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), unique=True, nullable=False)
    password = Column(String(60), nullable=False) # 60 is length of bcrypt hashes
    signup_ip = Column(Integer(unsigned=True), nullable=False) # TODO(2012-10-27) support IPv6
    time_created = Column(DateTime, nullable=False, default=datetime.utcnow())

    def __init__(self, username, password, signup_ip):
        self.username = username
        self.password = hashpw(password, gensalt())

        if isinstance(signup_ip, int):
            self.signup_ip = signup_ip
        else:
            self.signup_ip = inet_aton(signup_ip)


class UserEmail(Base):
    """An email address that's attached to a user account."""
    __tablename__ = 'user_email'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    time_created = Column(DateTime, nullable=False, default=datetime.utcnow())

    def __init__(self, user, email):
        if isinstance(user, int):
            self.user_id = user
        elif isinstance(user, str) or isinstance(user, unicode):
            user_id = DBSession.query(User.id).filter_by(username=user).first()
            self.user_id = user_id.id

        self.email = email


class State(Base):
    """U.S. state or Canadian province, territory, capitol, or other."""
    __tablename__ = 'state'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    abbreviation = Column(String(255), nullable=False)
    type = Column(String(255), nullable=False)


def get_park_types():
    return dict([
        ('IHS', 'International Historic Site'),
        ('NB', 'National Battlefield'),
        ('NBP', 'National Battlefield Park'),
        ('NBS', 'National Battlefied Site'),
        ('NHP', 'National Historical Park'),
        ('NHP & EP', 'National Historical Park and Ecological Preserve'),
        ('NHP & PRES', 'National Historical Park and Preserve'),
        ('NH RES', 'National Historical Reserve'),
        ('NHS', 'National Historic Site'),
        ('NHT', 'National Historic Trail'),
        ('NL', 'National Lakeshore'),
        ('NM', 'National Monument'),
        ('NM & PRES', 'National Monument & Preserve'),
        ('NMP', 'National Military Park'),
        ('N MEM', 'National Memorial'),
        ('NP', 'National Park'),
        ('N & SP', 'National and State Parks'),
        ('NP & PRES', 'National Park and Preserve'),
        ('N PRES', 'National Preserve'),
        ('NR', 'National River'),
        ('NRA', 'National Recreation Area'),
        ('NRR', 'National Recreation River'),
        ('NRRA', 'National River and Recreation Area'),
        ('N RES', 'Nation Reserve'),
        ('NS', 'National Seashore'),
        ('NSR', 'National Scenic River or Riverway'),
        ('NST', 'National Scenic Trail'),
        ('PKWY', 'Parkway'),
        ('SRR', 'Scenic and Recreational River'),
        ('WR', 'Wild River'),
        ('WSR', 'Wild and Scenic River'),
    ])


class Park(Base):
    """A park, national historic landmark, or other area administered by the
    National Park Service.
    """
    __tablename__ = 'park'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    url = Column(String(255), nullable=False, unique=True)
    state_id = Column(Integer, ForeignKey('state.id'))
    latitude = Column(Float)
    longitude = Column(Float)
    time_created = Column(DateTime, nullable=False, default=datetime.utcnow())
    date_founded = Column(Date)
    region = Enum('NA', 'MA', 'NC', 'SE', 'MW', 'SW', 'RM', 'W', 'PNWA', nullable=False)
    type = Enum(get_park_types().keys(), nullable=False)


    def __init__(self, name, state, url, region, type, latitude=None, longitude=None):
        self.name = name
        self.url = url
        self.region = region

        if isinstance(state, int):
            self.state_id = state
        elif isinstance(state, str) or isinstance(state, unicode):
            # Try both the name and the abbreviation
            self.state_id = DBSession.query(
                State.id
            ).filter(
                or_(
                    State.abbreviation == state,
                    State.name == state
                )
            ).scalar()

        self.latitude = latitude
        self.longitude = longitude


class Stamp(Base):
    """A passport park stamp."""
    __tablename__ = 'stamp'
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey('stamp_location.id'))
    text = Column(String(255), nullable=False)
    time_created = Column(DateTime, nullable=False, default=datetime.utcnow())
    type = Enum('normal', 'bonus', nullable=False)
    status = Enum('normal', 'lost', 'archived', nullable=False)


class StampCollection(Base):
    """A user has recorded a collection of a stamp."""
    __tablename__ = 'stamp_collection'
    id = Column(Integer, primary_key=True)
    stamp_id = Column(Integer, ForeignKey('stamp.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    time_collected = Column(DateTime, nullable=False, default=datetime.utcnow())
    time_created = Column(DateTime, nullable=False, default=datetime.utcnow())


class StampLocation(Base):
    """A location where stamps can be collected, e.g. a visitor's center."""
    __tablename__ = 'stamp_location'
    id = Column(Integer, primary_key=True)
    park_id = Column(Integer, ForeignKey('park.id'), nullable=False)
    description = Column(String(255))
    address = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)


class StampToLocation(Base):
    """One stamp can be at multiple locations. This is a junction table that
    stores that relationship.
    """
    __tablename__ = 'stamp_at_location'
    id = Column(Integer, primary_key=True)
    stamp_id = Column(
        Integer,
        ForeignKey('stamp.id'),
        nullable=False,
    )
    stamp_location_id = Column(
        Integer,
        ForeignKey('stamp_location.id'),
        nullable=False,
    )


class OperatingHours(Base):
    """The hours that a particular location are open for."""
    __tablename__ = 'operating_hours'
    id = Column(Integer, primary_key=True)
    location_id = Column(
        Integer,
        ForeignKey('stamp_location.id'),
        nullable=False,
    )
    day_of_week = Enum(
        'Sunday',
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        nullable=False
    )
    # For example, a place that is open 09:00-17:00 would have:
    # time_open: 09:00
    # minutes: 480
    # A place that is open 18:00-02:00 would have:
    # time_open: 18:00
    # minutes: 480
    time_open = Column(Time, nullable=False)
    minutes= Column(Integer, nullable=False)

    # This might need to be relaxed if a place closes mid day
    UniqueConstraint('location_id', 'day_of_week')
