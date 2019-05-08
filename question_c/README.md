
### Solution to Question C ###

Question: At Ormuco, we want to optimize every bits of software we write. Your goal is to write a new
          library that can be integrated to the Ormuco stack. Dealing with network issues everyday,
          latency is our biggest problem. Thus, your challenge is to write a new Geo Distributed LRU (Least
          Recently Used) cache with time expiration. This library will be used extensively by many of our
          services so it needs to meet the following criteria:
         
            1 - Simplicity. Integration needs to be dead simple.
            2 - Resilient to network failures or crashes.
            3 - Near real time replication of data across Geolocation. Writes need to be in real time.
            4 - Data consistency across regions
            5 - Locality of reference, data should almost always be available from the closest region
            6 - Flexible Schema
            7 - Cache can expire 
          As a hint, we are not looking for quantity, but rather quality, maintainability, scalability,
          testability and a code that you can be proud of.


#### Overall Design ####
The library is designed to be used in a distributed environment, that is an environment setup where there are multiple machines at [possibly] different geographical locations, all performing a common function, in this case, all acting as LRU caches.

The design uses a database as the interaction layer between all the caches in the environment and heavily uses [SQLAlchemy](https://www.sqlalchemy.org/) as the ORM mapper for interacting with the database. In a way, the architecture of the library is similar to a publish-subscribe based one (like Redis, MQTT) with the additional implementation of the required LRU cache abilities. The interaction layer (database) chosen for the library was PostgreSQL because of its clustering, pooling, and enterprise features that make it suitable for production. Consequently, it is required that a Postgres database is available prior to testing. If one isn't available, though, the library defaults to an SQLite database in the file's local directory. 

The library uses the geolocation (a latitude-longitude container) of the machine to be made a cache to instantiate the cache. That is, if a machine in Montreal, for example, is to be made a cache, the library requires that the latitude-longitude pair of the machine's location be used to instantiate the cache. i.e. `montreal_cache = GeoLRUCache((55.335666, -23.232355))`, where `55.335666` is the latitude and, `-23.232355` the longitude (not the actual latitude and longitude of Montreal). Other caches at different locations that use the library will instantiate their respective caches this way -- using the latitude and longitude pair of their respective locations. This is done in order to determine the cache nearest to this cache in the environment, so that when this cache sets a new item in itself and *propagates* the item to __all__ the other caches in the environment, the order with which the other caches will get the item will be according to their proximity to this cache. i.e. the closest cache to this cache first gets the item, then the second, then the third...etc. This is in order to achieve the *Locality of Reference* requirement. The distance between this cache and the other caches is achieved with the help of [Haversine's Formula](https://en.wikipedia.org/wiki/Haversine_formula) which uses their coordinates to determine their distances.

The use of a PostgreSQL database was also chosen in order to match the second requirement -- resilience to network failures or crashes. In a production environment, I imagine clusters of the database will be deployed in strategic locations to achieve redundancy and availability, regardless of network state.

The library uses a very light schema that just contains two tables. One to hold the geolocations (latitude-longitude pair) of all the caches registered in the environment, and the other to allow for communication between caches.

#### Testing ####
*Test Design*: In order to mimic the presence of machines in several geolocations, I had to test the library in a `mulitprocessing` environment. This is not to say that I used Python's `multiprocessing` library, as I could not get the `unittest` module to behave, but it's to state that I mocked each machine as a different, separate python script, running on a different, separate python terminal/cmd process. This was a made as a compromise. Kindly bear with me.

source directory: `question_c/`

- Install the libraries in the `requirements.txt` file (preferably in a virtual environment). (Mainly `sqlalchemy` and PostgreSQL's driver `psycopg2`). To do that, run `pip3 install -r requirements.txt`. 
- The question also requested that a library be created, like Question B, so I created a library, and as usual, did not upload to PyPi, the local installation method still proving effective enough. To install the library, run from the source directory, `pip3 install ./geo_lrucache/dist/GeoLRUCache-0.0.1-py3-none-any.whl`
- After installation, `cd` into the tests directory: `cd tests`
- Directions for testing are in the README.md file in the `tests` directory

#### Source Code Location ####
The actual source code of the library can be found in `./geo_lrucache/build/lib/lrucache` or `./geo_lrucache/lrucache`

