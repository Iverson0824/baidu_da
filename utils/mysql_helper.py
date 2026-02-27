import pymysql
from dbutils.pooled_db import PooledDB
import configparser
from contextlib import contextmanager


class MysqlHelper:
    # This variable acts as a 'storage slot' for our single instance
    _instance = None

    def __new__(cls, *args, **kwargs):
        '''
        THe Singleton Pattern:
        Before creating a new object, check if we already have one.
        If yes, return the existing one.
        If no, create new one and store it.
        '''
        if not cls._instance:
            # if no instance exists,
            # create it using the parent's (super) __new__ method
            cls._instance = super(MysqlHelper, cls).__new__(cls)
            # Setting up  the connection pool for this new instance
            cls._instance._init_pool()
        return cls._instance

    def _init_pool(self):
        '''
        Reads the .ini file and builds the pool of connections
        '''
        config = configparser.ConfigParser()
        config.read('config/db_config.ini')

        # Pull the data from the [mysql] section
        db_params = dict(config['mysql'])

        # The port in .ini file is text, but MySQL needs it as number
        db_params['port'] = int(db_params['port'])

        # Create the PooledDB instance
        self.pool = PooledDB(
            creator=pymysql,    # Use the pymysql driver
            maxconnections=10,  # Maximum number of connections
            mincached=2,        # Keep 2 connections ready even if not in use
            blocking=True,      # Block if no connection is available
                                # (If all in use, wait until one is free)
            **db_params         # Pass the database parameters from .ini file
        )
        print('Connection pool ready')

    def select_all(self, sql, params=None):
        '''
        A Helper method to fetch data using the context manager
        '''
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()

    def execute_sql(self, sql, params=None):
        """
        Used for single queries: INSERT, UPDATE, DELETE.
        Handles Commit and Rollback automatically.
        """
        conn = self.pool.connection()
        cursor = conn.cursor()

        try:
            affected_rows = cursor.execute(sql, params)
            conn.commit()
            return affected_rows
        except Exception as e:
            conn.rollback()
            print(f'Error executing SQL: {e}')
            return 0
        finally:
            cursor.close()
            conn.close()

    @contextmanager
    def get_cursor(self):
        """
        The industry standard way to handle connections safely.
        Automatically borrows and returns connections, even if errors occur.
        """
        conn = self.pool.connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        try:
            yield cursor    # yield cursor to user's code
        finally:
            cursor.close()
            conn.close()

    @contextmanager
    def transaction(self):
        """
        A context manager for MULTIPLE queries that need
        to be in a single transaction. Commits all automatically
        if successful, rolls back everything if any query fails.
        """
        conn = self.pool.connection()
        cursor = conn.cursor()

        try:
            yield cursor     # give user cursor to run multiple execute()
            conn.commit()    # Commit the transaction after runs successfully
        except Exception as e:
            conn.rollback()  # Roll back changes if error happened
            raise e          # Re-raise the error so script knows it failed
        finally:
            cursor.close()
            conn.close()
