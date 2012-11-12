import re

from datetime import datetime
from bcrypt import gensalt
from bcrypt import hashpw
from socket import inet_aton
from sqlalchemy import Binary
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import or_
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.util import buffer
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


class UserEmail(Base):
    """An email address that's attached to a user account."""
    __tablename__ = 'user_email'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False) 
    email = Column(Text, unique=True, nullable=False)
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
    name = Column(Text, nullable=False, unique=True)
    url = Column(Text, nullable=False, unique=True)
    state_id = Column(Integer, ForeignKey('state.id'), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    time_created = Column(DateTime, nullable=False, default=datetime.utcnow())
    region = Enum('NA', 'MA', 'NC', 'SE', 'MW', 'SW', 'RM', 'W', 'PNWA')
    type = Enum(get_park_types().keys(), nullable=False)


    def __init__(self, name, state, url, region, type, latitude=None, longitude=None):
        self.name = name
        self.url = url
        self.region = region

        if isinstance(state, int):
            self.state_id = state
        elif isinstance(state, str) or isinstance(state, unicode):
            # Try both the name and the abbreviation
            state_id = DBSession.query(
                State.id
            ).filter(
                or_(
                    State.abbreviation == state,
                    State.name == state
                )
            ).scalar()
            if state_id is None:
                state_id = DBSession.query(State.id).filter_by(abbreviation=state).scalar()
            self.state_id = state_id

        self.latitude = latitude
        self.longitude = longitude


class Stamp(Base):
    """A passport park stamp."""
    __tablename__ = 'stamp'
    id = Column(Integer, primary_key=True)
    park_id = Column(Integer, ForeignKey('park.id'), nullable=False)
    location = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    text = Column(Text, nullable=False)
    time_created = Column(DateTime, nullable=False, default=datetime.utcnow())

    def __init__(self, park, text):
        if isinstance(park, int):
            self.park_id = park
        elif isinstance(park, str) or isinstance(park, unicode):
            park_id = DBSession.query(Park.id).filter_by(name=park).first()
            self.park_id = park_id.id

        self.text = text


class StampCollection(Base):
    """A user has recorded a collection of a stamp."""
    __tablename__ = 'stamp_collection'
    id = Column(Integer, primary_key=True)
    stamp_id = Column(Integer, ForeignKey('stamp.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    time_collected = Column(DateTime, nullable=False, default=datetime.utcnow())
    time_created = Column(DateTime, nullable=False, default=datetime.utcnow())
