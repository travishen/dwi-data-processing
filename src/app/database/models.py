from sqlalchemy import (
    Integer,
    Column,
    Sequence,
    Unicode,
    Date,
    Boolean,
    Float,
    UniqueConstraint
)
from . import _base


class CountryTown(_base):
    __tablename__ = 'country_town'
    id = Column(Integer, Sequence('country_town_id_seq'), primary_key=True, nullable=False)
    country = Column(Unicode(length=30), nullable=False)
    town = Column(Unicode(length=30), nullable=False)
    code = Column(Unicode(length=8))

    __table_args__ = (
        UniqueConstraint('country', 'town', 'code', name='country_town_unique_constraint'),
     )


class Violation(_base):
    __tablename__ = 'violation'
    id = Column(Integer, Sequence('violate_id_seq'), primary_key=True, nullable=False)
    uid = Column(Unicode(length=12), nullable=False)
    birthday = Column(Date)
    date = Column(Date, nullable=False)

    is_recidivist = Column(Boolean)
    is_patched = Column(Boolean)

    # one to one relationships
    accident_id = Column(Integer)


class Accident(_base):
    __tablename__ = 'accident'
    id = Column(Integer, Sequence('accident_id_seq'), primary_key=True, nullable=False)
    date = Column(Date, nullable=False)
    hour = Column(Integer, nullable=False)
    dead = Column(Integer, nullable=False)
    injured = Column(Integer, nullable=False)
    party_no = Column(Integer, nullable=False)
    gender_no = Column(Integer, nullable=False)
    uid = Column(Unicode(length=30), nullable=False)
    driver_birthday = Column(Date)
    birthday = Column(Date)
    is_birthday_patched = Column(Boolean, default=False)
    country = Column(Unicode(length=30), nullable=False)
    town = Column(Unicode(length=30), nullable=False)
    party_address_code = Column(Unicode(length=8))
    party_country = Column(Unicode(length=30))
    party_town = Column(Unicode(length=30))
    is_party_address_patched = Column(Boolean, default=False)
    car_type = Column(Unicode(length=3), nullable=False)
    injury_level = Column(Integer, nullable=False)
    driver_level = Column(Integer, nullable=False)
    drunk_level = Column(Integer, nullable=False)
    hit_and_run = Column(Integer, nullable=False)
    job = Column(Integer, nullable=False)
    cause_type = Column(Integer)
    age = Column(Integer)
    age_group = Column(Integer)

    # one to one relationships
    violation_id = Column(Integer)

    __table_args__ = (
        UniqueConstraint('uid', 'date', 'hour', name='accident_unique_constraint'),
     )


class Divorce(_base):
    __tablename__ = 'divorce'
    id = Column(Integer, Sequence('divorce_id_seq'), primary_key=True, nullable=False)
    address_code = Column(Unicode(length=8))
    year = Column(Integer, nullable=False)
    rate = Column(Float, nullable=False)


class Old(_base):
    __tablename__ = 'old'
    id = Column(Integer, Sequence('old_id_seq'), primary_key=True, nullable=False)
    address_code = Column(Unicode(length=8))
    year = Column(Integer, nullable=False)
    rate = Column(Float, nullable=False)


class Indigenous(_base):
    __tablename__ = 'indigenous'
    id = Column(Integer, Sequence('indigenous_id_seq'), primary_key=True, nullable=False)
    address_code = Column(Unicode(length=8))
    year = Column(Integer, nullable=False)
    rate = Column(Float, nullable=False)


class Education(_base):
    __tablename__ = 'education'
    id = Column(Integer, Sequence('education_id_seq'), primary_key=True, nullable=False)
    address_code = Column(Unicode(length=8))
    year = Column(Integer, nullable=False)
    rate = Column(Float, nullable=False)


class IncomeMid(_base):
    __tablename__ = 'income_mid'
    id = Column(Integer, Sequence('income_id_seq'), primary_key=True, nullable=False)
    address_code = Column(Unicode(length=8))
    year = Column(Integer, nullable=False)
    rate = Column(Float, nullable=False)


class IncomeAvg(_base):
    __tablename__ = 'income_avg'
    id = Column(Integer, Sequence('income_id_seq'), primary_key=True, nullable=False)
    address_code = Column(Unicode(length=8))
    year = Column(Integer, nullable=False)
    rate = Column(Float, nullable=False)
