
from lrucache.geo_lrucache import GeoLRUCache
from helper import TEST_DB_URL

import time


# Manitoba's Latitude and Longitude = 54.1647018,-104.4399657
print("This is Manitoba's Cache")

cache = GeoLRUCache((54.1647018,-104.4399657), db_url=TEST_DB_URL)

print("I published ('from_manitoba_cache', 'manitoba_set') to every cache in the environment")
cache["from_manitoba_cache"] = "manitoba_set"  # or cache.set("from_manitoba_cache", "manitoba_set")

n = 0
while 1:

    all_keys = ["from_quebec_cache", "from_alberta_cache", "from_nfl_cache", "from_bc_cache"]

    print()
    print('-'*50)
    for key in all_keys:
        val = cache.get(key)
        if val:
            print(f"Got item ({key}, {val})")

        # If the item does not exist, None is printed. None is also
        # printed if the item has expired in the cache        
        else:
            print("None")
    print('-'*50)      
    print()      

    # Stop the script after eighty seconds. The default expiry time of items in the cache
    # is sixty seconds. This is done to also test cache expiry.
    if n == 80:
        break

    n += 1
    time.sleep(1)