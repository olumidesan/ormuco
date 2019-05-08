
### Testing ###
*Test Design*: To mock different machines located at different regions, I created five scripts to mock each region. Each script being                    made to act like it's a machine at a separate geolocation. The five regions I chose were: Quebec (because Ormuco is in 
               Quebec :), Manitoba, Alberta, NewFoundland and Labrador, and British Columbia. The accurate geolocations of each province was gotten through Google Maps and was used as the coordinates for creating (instantiating) each cache.

In this test, the cache from Manitoba is to be started last using the below procedure. This is because the script in the `manitoba_test.py` file requires that the other caches, `alberta_test.py`, `nfl_test.py`, `bc_test.py`, and `quebec_test.py` have all registered themselves in the environment before Manitoba's cache sets an item in itself. If any of the others is not started before the Manitoba's cache, it won't see the set operation that Manitoba's cache propagated.

**The `helper.py` file is simply a, well, helper file that provides, for this test, the `db_url` string format to be used for connecting the cache to the PostgreSQL database on instance creation. If also using Postgres, change the parameters in the `helper.py` file to match your Postgres setup. When instantiating the cache, the `db_url` is an optional keyword argument. An example of cache instantiation with the `db_url` argument is:
`quebec_cache = GeoLRUCache((52.4430825,-86.2679867), db_url='postgresql+psycopg2://olumide:secretpassword@127.0.0.1:5432/ormuco')`
Again, if none is supplied, the library defaults to an SQLite database. See Notes and Warnings below**

The test tests for two things:
1. That when a cache in one geolocation sets an item on itself, the other caches registered in the environment see that operation and also set that item within themselves (data consistency), in the order of their proximity to the cache that set the item on itself.
2. That the cache expires after it's set to expire (the value of the keyword argument, `expires_in`, which defaults to one minute)

Directory: `ormuco/question_c/tests`

- Fire up five bash terminals, all into the virtual environment where `sqlalchemy`, `psycopg2`, and the `lrucache` were installed into. 
- Run each of the location's script in each of the terminals, starting `manitoba_test.py` last.
- Watch the library work.

##### Notes and Warnings #####
1. As the database is the main interaction layer between all the caches, it is important that it's an enterprise grade database being used for production. This test has only been carried out using PostgreSQL and SQLite. However, note that if SQLite is being used, it must be used cautiously, as it doesn't support concurrent writes. Using this manual method of starting each machine, though, SQLite also works because it becomes impossible to start each script at the same time.
2. The GeoLRUCache is meant to be a singleton class, meaning that only one instance of the cache is meant to be created per process. Even if this singleton behaviour was not implemented, it's worth mentioning, as instantiating more than one GeoLRUCache instance will indeterminately cause write conflicts when accessing the database, since no locking mechanism was used for the listener and main thread of the instance, who by themselves never have conflict but may do when another instance is created within the same process.
3. To test which cache actually gets each newly propagated item first, the `propagate_write` decorator in `./geo_lrucache/lrucache/utils.py` file can be modified on line `172` where a sleep call has been commented out. Uncommenting that line and running the test using the local code in the `./geo_lrucache/lrucache` folder will give visual notification of which location is closest to Manitoba, and consequently who gets the item first (locality of reference)
