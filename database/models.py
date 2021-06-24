from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

favorite_stop_user = Table(
    "favorite_stops_users",
    Base.metadata,
    Column("stop_id", Integer, ForeignKey("stops.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
)

cached_stop_user = Table(
    "cached_stops_users",
    Base.metadata,
    Column("stop_id", Integer, ForeignKey("stops.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
)

# The Stop class is compatible with the one used in bus.gal-api. Basically they use the same name for parameters

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    state = Column(String)
    favorite_stops = relationship("Stop", secondary=favorite_stop_user)
    cached_stops = relationship("Stop", secondary=cached_stop_user)
    expedition = relationship("Expedition", uselist=False)


class Stop(Base):
    __tablename__ = "stops"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    type_id = Column(Integer)

class Expedition(Base):
    __tablename__ = "expeditions"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key = True)
    origin_id = Column(Integer, ForeignKey("stops.id"))
    origin = relationship("Stop", foreign_keys=[origin_id])
    destination_id = Column(Integer, ForeignKey("stops.id"))
    destination = relationship("Stop", foreign_keys=[destination_id])
    date = Column(String)
