from datetime import datetime
from datetime import date
from bcrypt import gensalt
from bcrypt import hashpw
from sqlalchemy import BigInteger
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Date
from sqlalchemy import Time
from sqlalchemy import Enum
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Index
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
    # We could use an unsigned integer here, but it's deprecated
    signup_ip = Column(BigInteger, nullable=False) # TODO(2012-10-27) support IPv6
    time_created = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, username, password, signup_ip):
        self.username = username
        self.password = hashpw(password, gensalt())

        if isinstance(signup_ip, int):
            self.signup_ip = signup_ip
        else:
            self.signup_ip = reduce(lambda a, b: a << 8 | b, map(int, signup_ip.split('.')))


class UserEmail(Base):
    """An email address that's attached to a user account."""
    __tablename__ = 'user_email'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    time_created = Column(DateTime, nullable=False, default=datetime.utcnow)

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
        ('NHA', 'National Heritage Area'), # Not in the stamp book
        ('NHC', 'National Heritage Corridor'), # Not in the stamp book
        ('NHP', 'National Historical Park'),
        ('NHP & EP', 'National Historical Park and Ecological Preserve'),
        ('NHP & PRES', 'National Historical Park and Preserve'),
        ('NH RES', 'National Historical Reserve'),
        ('NHS', 'National Historic Site'),
        ('NHT', 'National Historic Trail'),
        ('NL', 'National Lakeshore'),
        ('NM', 'National Monument'),
        ('NM & PRES', 'National Monument and Preserve'),
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
        ('N RES', 'National Reserve'),
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
    state_id = Column(Integer, ForeignKey('state.id'), nullable=False)
    latitude = Column(Float)
    CheckConstraint('latitude >= -90 and latitude <= 90')
    longitude = Column(Float)
    CheckConstraint('longitude >= -90 and longitude <= 90')
    time_created = Column(DateTime, nullable=False, default=datetime.utcnow)
    date_founded = Column(Date)
    region = Column(Enum('NA', 'MA', 'NC', 'SE', 'MW', 'SW', 'RM', 'W', 'PNWA'), nullable=False)
    type = Column(Enum(*get_park_types().keys()))
    added_by_user_id = Column(Integer, ForeignKey('user.id'))


    def __init__(self, name, state, url, region, type, latitude=None, longitude=None, date_founded=None):
        self.name = name

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

        self.url = url
        self.region = region
        self.type = type
        self.latitude = latitude
        self.longitude = longitude
        self.date_founded = date_founded


class Stamp(Base):
    """A passport park stamp."""
    __tablename__ = 'stamp'
    id = Column(Integer, primary_key=True)
    text = Column(String(255), nullable=False)
    time_created = Column(DateTime, nullable=False, default=datetime.utcnow)
    time_updated = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    type = Column(Enum('normal', 'bonus'), nullable=False)
    status = Column(Enum('active', 'lost', 'archived'), nullable=False)
    added_by_user_id = Column(Integer, ForeignKey('user.id'))


class StampHistory(Base):
    """A history of stamp edits."""
    # TODO(bskari|2013-08-24) This should be stored in a log or something
    # instead of the database
    __tablename__ = 'stamp_history'
    id = Column(Integer, primary_key=True)
    stamp_id = Column(Integer, ForeignKey('stamp.id'))
    text = Column(String(255), nullable=False)
    time_created = Column(DateTime, nullable=False, default=datetime.utcnow)
    type = Column(Enum('normal', 'bonus'), nullable=False)
    status = Column(Enum('active', 'lost', 'archived'), nullable=False)
    edited_by_user_id = Column(Integer, ForeignKey('user.id'))


class StampCollection(Base):
    """A user has recorded a collection of a stamp."""
    __tablename__ = 'stamp_collection'
    id = Column(Integer, primary_key=True)
    # I could just record the StampToLocation id, but then I would have to
    # use a flag for 'active' so that I could remove StampToLocation entries
    # when stamps are lost or removed from a location. Recording the stamp_id
    # and park_id seems like a cleaner plan.
    stamp_id = Column(Integer, ForeignKey('stamp.id'), nullable=False)
    park_id = Column(Integer, ForeignKey('park.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    date_collected = Column(Date, nullable=False, default=date.today)
    time_created = Column(DateTime, nullable=False, default=datetime.utcnow)

Index('idx_user_id', StampCollection.user_id)
Index('idx_stamp_id', StampCollection.stamp_id)


class StampLocation(Base):
    """A location where stamps can be collected, e.g. a visitor's center."""
    __tablename__ = 'stamp_location'
    id = Column(Integer, primary_key=True)
    park_id = Column(Integer, ForeignKey('park.id'), nullable=False)
    description = Column(String(255), nullable=False)
    address = Column(String(255))
    latitude = Column(Float)
    CheckConstraint('latitude >= -90 and latitude <= 90')
    longitude = Column(Float)
    CheckConstraint('longitude >= -180 and longitude <= 180')
    added_by_user_id = Column(Integer, ForeignKey('user.id'))
    time_created = Column(DateTime, nullable=False, default=datetime.utcnow)

# Index by longitude first because the US is more wide than it is tall.
# I don't know if that will even matter, considering that longitude is
# probably going to be unique anyway.
Index('idx_longitude_latitude', StampLocation.longitude, StampLocation.latitude)


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
    UniqueConstraint('stamp_id', 'stamp_location_id')
    time_created = Column(DateTime, nullable=False, default=datetime.utcnow)


class OperatingHours(Base):
    """The hours that a particular location are open for."""
    __tablename__ = 'operating_hours'
    id = Column(Integer, primary_key=True)
    location_id = Column(
        Integer,
        ForeignKey('stamp_location.id'),
        nullable=False,
    )
    day_of_week = Column(
        Enum(
            'Sunday',
            'Monday',
            'Tuesday',
            'Wednesday',
            'Thursday',
            'Friday',
            'Saturday',
        ),
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
