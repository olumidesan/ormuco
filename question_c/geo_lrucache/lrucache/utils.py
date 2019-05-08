
import math
import time

from functools import wraps


EARTH_RADIUS = 6378137 

def rad(coordinate):
    return (math.pi * coordinate) / 180


def get_distance(location_1, location_2):
     """

     Haversine Formula: https://en.wikipedia.org/wiki/Haversine_formula

     This function returns the distance between two decimal-degree coordinates. 
     The coordinates are a tuple of the latitude and longitude of the location.

     """

     lat_1, long_1 = location_1
     lat_2, long_2 = location_2

     lat_dist = rad(lat_2 - lat_1)
     long_dist = rad(long_2 - long_1)

     a = (math.sin(lat_dist / 2) * math.sin(lat_dist / 2)) + math.cos(rad(lat_1)) * math.cos(rad(lat_2)) * \
          math.sin(long_dist / 2) * math.sin(long_dist / 2)

     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

     distance = EARTH_RADIUS * c

          
     return round(distance, 5)


def validate_coordinates(coordinates):
     """
     This function helps to validate the inputed coordinates
     The coordinates must be a 2-length container of floats, where
     the first item is the latitude and the other, the longitude

     """
     # Each coordinate should be a tuple of length 2, and 
     # must contain truthy values
     if len(coordinates) == 2 and all(coordinates):
          try:
               # Both items must be "floatable"
               [float(i) for i in coordinates]
               return True
          except ValueError:
               return False
               
     else:
          return False


def clean_up(func):
     """
     Decorator function that 'cleans up' the cache before every
     major operation (setting, getting, etc.). The function
     deletes all expired caches and deletes the oldest item
     in the cache once the cache's maximum size is reached.

     """
     @wraps(func)
     def wrapper(self, *args, **kwargs):
          # If the items in the cache do expire
          if self.expires_in is not None:

               # Get the current time
               now = int(time.time())

               # A list of all the keys to delete 
               # once they have been identified
               keys_to_delete = []

               # Check the times to live of all the items in the cache,
               # and delete the items that have expired. To prevent
               # deleting while iterating, add the expired keys to a list.
               for key in self.times_to_live:
                    if self.times_to_live[key] < now:
                         keys_to_delete.append(key)
               
               # Then, delete the items using their keys 
               for key in keys_to_delete:    
                    self.__delitem__(key)

          # Check if the maximum size of the cache has been reached,
          # delete the oldest one. Ordered dicts retain item insertion
          # order. Leverage on that
          if (len(self.values) > self.max_size):
               oldest_datum = self.access_times.popitem(last=False)
               self.__delitem__(oldest_datum[0])

               # Keep a copy of the oldest item in the cache, just in case
               # of a future API requirement
               self.set_oldest_item = oldest_datum

          # If the size of the cache is still less than the cache's maximum size,
          # still save the first item in the cache as the oldest item
          else:
               try:
                    # try to get the first item that was saved in the cache
                    first_item = next(iter(self.access_times.items()))
                    # Save the item as the oldest item in the cache
                    self.set_oldest_item = (first_item[0], self.values.get(first_item[0]))

               # if no item has ever been saved, use the default settings (None)
               except StopIteration:
                    self.set_oldest_item
             
          return func(self, *args, **kwargs)
     return wrapper



def propagate_write(func):
     """
     This function propagates every write operation across all caches 
     registered with the application. The database is the interaction
     layer between each cache and the other caches. 

     The function propagates the writes linearly, in a closest-to-furthest
     manner, meaning that the closest cache to this cache will be written
     to first. This is done to achieve the _locality of reference_ requirement.
     It calculates the caches nearest to it by using the get_distance function, 
     and then it sorts it from smallest to largest.

     Basically, 'publish'.

     """
     @wraps(func)
     def wrapper(self, key, value, *args, **kwargs):
          """
          :param self: the instance object of the cache
          :param key: the key of the item being set by the cache
          :param value: the value of the item being set by the cache
          :param *args: a tuple of optional positional arguments
          :param *kwargs: a dictionary of all optional keyword arguments
                          may sometimes contain "from_thread: True", which
                          signifies that this function was called from a 
                          background thread
          """

          # The writes should only propagate to all the other caches in the system
          # if the operation of item setting (i.e. __setitem__) came from the main
          # cache's thread and not a background thread.
          if kwargs.get("from_thread") is None:
               
               # Get a list of all the caches registered in the environment, 
               # arranged according to their distance to this cache 
               prioritized_distance_index = self.sort_distances()

               # For each coordinate-distance tuple in the above list, save the key and value to the database.
               # This will trigger the other caches (who are by default listening on the database) to read the
               # key and value and save it on themselves.
               # The first item in the list is the cache closest to this cache, the next item is the cache 
               # second-closest to this cache, and so on. That way, data will always first be available from
               # the cache closest to this cache (locality of reference).
               for i in prioritized_distance_index:
                    new_set = CacheDataStore(latitude=i[0][0], longitude=i[0][1], key=key, value=value)
                    try:
                         self.session.add(new_set)
                         self.session.commit()
                         # To test which location first receives the data being propagated,
                         # uncomment the sleep() call below.
                         # time.sleep(5)
                    except:
                         self.session.rollback()

          return func(self, key, value, *args, **kwargs)
     return wrapper
          

from .models import CacheGeolocation, CacheDataStore