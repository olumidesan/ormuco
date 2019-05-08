
import os
import time
import json
import threading

from collections import OrderedDict

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import CacheGeolocation, CacheDataStore, Base, DB_NAME
from .utils import validate_coordinates, get_distance, clean_up, propagate_write

my_dir = os.path.abspath(os.path.dirname(__file__))



class InvalidCoordinatesError(Exception):
    pass


class GeoLRUCache:
    """
    A geolocation-based LRUCache with optional time expiration. Geolocation is 
    implemented using coordinates, i.e. a (latitude, longitude) pair

    All distributed caches MUST provide the same db_url argument upon instantiation
    to allow for interaction between themselves.

    """

    DEFAULT_DATABASE_URL = 'sqlite:///' + os.path.join(my_dir, DB_NAME + '.db')

    def __init__(self, coordinates, max_size=1024, expires_in=1*60, db_url=None):
        """
        :param coordinates: the latitude-longitude pair of the cache's location
        :param max_size: the maximum number of items the cache can store before
                         removing the oldest item. Defaults to 1024 items.
        :param expires_in: the time-to-live (in seconds) of each item in the cache.
                           defaults to one minute (60 seconds)

        :param db_url: the database url (in SQLAlchemy connection string format) that 
                       the cache connects to to synchronize itself with other caches
                       in a distributed environment. Please visit this site for help
                       http://docs.sqlalchemy.org/en/latest/core/engines.html, on the
                       format of the string to be supplied. If none is supplied, it 
                       defaults to an sqlite database in the file's working directory.

        -------------------------------------------------------------------------------
        ---------------------------------*Future Upgrade*------------------------------
        :param neighbour_aware: Boolean keyword argument to make the cache aware of its 
                                nearest neighbour. If True, when an item is requested 
                                from the cache and it does not have said item, it asks 
                                its nearest neigbour for the item, all within a specified
                                timeout period. If the nearest neighbour has the item, it 
                                returns the item, else it returns None.
        
        :param neighbour_request_timeout: time, in seconds, within which a request to the cache's
                                          nearest neighbour must be completed before the request
                                          times out.
        ----------------------------------------------------------------------------------------
        ----------------------------------------------------------------------------------------

        """
        
        if not validate_coordinates(coordinates):
            raise InvalidCoordinatesError("Coordinates must be a 2-length container of floats (or 'floatable' strings)")

        if db_url is None:
            self.db_url = GeoLRUCache.DEFAULT_DATABASE_URL
        else:
            self.db_url = db_url

        try:
            self.engine = create_engine(self.db_url)
        except Exception:
            raise

        self.coordinates = tuple(coordinates)
        self.max_size = max_size
        self.expires_in = expires_in
        
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Create the tables in the database if they don't already exist
        #try:
        Base.metadata.create_all(self.engine)
        # except:
        #     pass

        self.__values = dict()
        self.__access_times = OrderedDict()
        self.__times_to_live = OrderedDict()
        self.__oldest_item = None
        
        self.listener_thread = threading.Thread(target=self.listener, daemon=True)
        self.listener_thread.start()

    def listener(self):
        """
        Background thread that does two things:
        1: On cache creation, registers itself to the application in the 
           distributed environment, through the database.
        2: Constantly looks out for updates to any cache in the environment,
           through the database, so it can update itself accordingly (data consistency)
        """

        # Register cache to application on instance creation.
        # Basically, means 'subscribing' to receive messages
        session = self.Session()
        new_cache = CacheGeolocation(latitude=self.coordinates[0], longitude=self.coordinates[1])
        session.add(new_cache)
        session.commit()

        # Perpetually listen for writes to the database. Leverage on database read concurrency
        while True:
            new_item = session.query(CacheDataStore).filter(CacheDataStore.latitude == self.coordinates[0]).\
                               filter(CacheDataStore.longitude == self.coordinates[1]).first()

            if new_item is not None:
                # Get the key and value that was recently propagated
                key, value = new_item.key, new_item.value 

                # Save the item just recently propagated to the cache.
                # Signify the cache that this operation was done from
                # a background thread
                self.__setitem__(key, value, from_thread=True)

                # Once set, delete the database row, as it has been consumed
                session.delete(new_item)
                session.commit()

            # Be nice on the CPU
            time.sleep(0.5)  
        
        return


    @property
    def access_times(self):

        return self.__access_times

    @property
    def times_to_live(self):

        return self.__times_to_live
    
    @property
    def values(self):

        return self.__values

    @property
    def oldest_item(self):

        return self.__oldest_item

    @oldest_item.setter
    def set_oldest_item(self, item=None):

        self.__oldest_item = item
        return


    def empty(self):
        """
        Empties the cache

        """

        self.__oldest_item = None
        self.__values.clear()
        self.__access_times.clear()
        self.__times_to_live.clear()

        return
    
    @clean_up
    def size(self):

        return len(self.__values)

    @clean_up
    def __contains__(self, key):
        """
        Checks if a key is present in the cache

        :param key: the key of the item whose presence is to be checked
        :return: returns True or False depending on whether or not the
                 item is present.
        """

        if self.__values.get(key) is not None:
            return True

        return False 


    def sort_distances(self):

        # A list containing the distances of all the caches registered on the application
        # to this cache
        distance_index = []               

        # Get all the caches registered with the application
        caches = self.session.query(CacheGeolocation).all() 

        # Add the distance between this cache and each cache to the distance_index list
        for i in caches:
            # No need to add this cache's coordinates 
            if self.coordinates != (i.latitude, i.longitude):
                distance_to_me = get_distance(self.coordinates, (i.latitude, i.longitude))
                # Add it as a tuple of the cache's coordinates and its distance to this cache
                distance_index.append(((i.latitude, i.longitude), distance_to_me))

        # Sort the cache to get the cache closest to, furthest to this cache
        sorted_distances = sorted(distance_index, key=lambda i: i[1])     

        return sorted_distances


    def set(self, key, value):
        """
        Allows a .set(key, value) operation on the cache instance

        :param key: key to set the item with on the cache
        :param value: value of the item to set on the cache

        """

        return self.__setitem__(key, value)


    @propagate_write
    @clean_up
    def __setitem__(self, key, value, from_thread=False):
        """
        Create a new item in the cache using the key, value pair

        :param key: key to set the item with on the cache
        :param value: value of the item to set on the cache
        :param from_thread: keyword argument to differentiate when a write operation
                            is being done from a background thread or the main thread

        """        
        
        now = int(time.time())

        self.__delitem__(key)
        self.__values[key] = value
        self.__access_times[key] = now
        self.__times_to_live[key] = now + self.expires_in

        return

    def get(self, key):
        """
        Allows the .get(key) dict-like operation on the cache instance

        :param key: key of item to get from within the cache
        :return: returns the value of the item accessed, if it's present,
                 else None

        """

        return self.__getitem__(key)

    @clean_up
    def __getitem__(self, key):
        """
        Get an item from the cache using its key. 

        :param key: key of item to get from within the cache
        :return: returns the value of the item accessed, if it's present,
                 else None
        """
        now = int(time.time())

        if self.__values.get(key) is not None:
            del self.__access_times[key]
            self.__access_times[key] = now

        return self.__values.get(key)

    
    def __delitem__(self, key):
        """
        Delete an item from within the cache using its key

        :param key: key of item to delete from the cache

        """        
        if self.__values.get(key):
            self.__values.pop(key, None)
            self.__access_times.pop(key, None)
            self.__times_to_live.pop(key, None)
        
        return

    @clean_up
    def __repr__(self):
        """
        Convinience function that returns an API-like description
        of the cache. Simply added in case of a future API-requirement.

        """        
        cache = {
            'number_of_items': len(self.__values),
            'coordinates': self.coordinates,
            'oldest_item': self.__oldest_item,
            'maximum_size': self.max_size,
            'each_item_expires_in': self.expires_in,
            'items': {k:v for k,v in self.__values.items()}
        }

        return json.dumps(cache)
        



        
