
# Database settings for PostgresSQL
DB_NAME = 'ormuco'
DB_TYPE = 'postgresql'
DB_DRIVER = 'psycopg2'
DB_USER = 'postgres'
DB_PASSWORD = 'mysupersecretpassword'
DB_HOST = '127.0.0.1'
DB_PORT = '5432'

# Standard connection string format for SQLAlchemy's use
TEST_DB_URL = f"{DB_TYPE}+{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
