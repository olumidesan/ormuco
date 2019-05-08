


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean


DB_NAME = 'ormuco'

Base = declarative_base()


class CacheGeolocation(Base):
     """
     This table keeps hold of the coordinates of 
     all caches registered with the application

     """
     __tablename__ = 'caches_geolocation'

     id = Column(Integer, primary_key=True)
     latitude = Column(Float)
     longitude = Column(Float)


class CacheDataStore(Base):
     """
     This table holds the key and value of whichever
     cache sets, and is where every other cache will 
     read from (consume) to save to itself

     """

     __tablename__ = 'datastore'

     id = Column(Integer, primary_key=True)
     latitude = Column(Float)    
     longitude = Column(Float)
     key = Column(String(64))
     value = Column(String(64))
