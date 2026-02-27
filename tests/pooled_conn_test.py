from utils.mysql_helper import MysqlHelper

# 1. Try to create 2 separate 'objects'
db1 = MysqlHelper()
db2 = MysqlHelper()

# id() gives the memory address of the object
# if the ids are the same, it means they are the same object
print(f'Memory address of db1: {id(db1)}')
print(f'Memory address of db2: {id(db2)}')

if id(db1) == id(db2):
    print(f'Only one connection pool is created')
else:
    print(f'2 connection pools are created')

# 2. Try to fetch data using the helper
print(f'query testing')

try:
    sql_query = 'SELECT VERSION() as version;'
    result = db1.select_all(sql_query)

    if result:
        print(f"Database version: {result[0]['version']}")
        print(f'Successfully connected to MySQL')
    else:
        print(f'No results found')

except Exception as e:
    print(f'Error: {e}')

db = MysqlHelper()

# Create a test table
create_table_sql = """
CREATE TABLE IF NOT EXISTS test_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active'
);
"""
db.execute_sql(create_table_sql)
print("Test table ready.")

# Insert a user
insert_sql = "INSERT INTO test_users (username) VALUES (%s);"
# Using params (%s) prevents "SQL Injection" - a major security risk!
rows = db.execute_sql(insert_sql, ("Iverson",)) 
print(f"Inserted {rows} user.")

# Verify the insert
users = db.select_all("SELECT * FROM test_users;")
print(f"Current Users in DB: {users}")
    