import pymysql

config = {
    'host': 'localhost',
    'user': 'baidu_da',
    'password':'1!Asdfghjkl',
    'database':'practice_db',
    'charset':'utf8mb4',
    'cursorclass':pymysql.cursors.DictCursor  # This return the results as dictionaries
}

try:
    # First establish the connection
    connection = pymysql.connect(**config)
    print(f'Connected to MySQL database')
    
    try:
        # Create the cursor
        with connection.cursor() as cursor:
            # Getting database version
            cursor.execute('SELECT VERSION()')
            version = cursor.fetchone()
            print(f'database version:{version["VERSION()"]}')

            # Drop table if exists
            cursor.execute('DROP TABLE IF EXISTS students')

            # Create table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    student_id INT AUTO_INCREMENT PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    enrollment_date DATE DEFAULT(CURRENT_DATE()),
                    gpa DECIMAL(3, 2) CHECK (
                        gpa >= 0.00
                        AND gpa <= 4.00
                    ),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE = InnoDB
            ''')
            print(f'Table created')

            # Insert data
            cursor.execute('''
                INSERT INTO students (first_name, last_name, email, gpa)
                VALUES
                    ('Iverson', 'Chen', 'iverson3chenai@icloud.com', 4.00),
                    ('Rebecca', 'Zhang', 'zhangyuhan1202@gmail.com', 3.99)
            ''')
            print(f'Data inserted')

            sql = '''
                INSERT INTO students(first_name, last_name, email, gpa) VALUES (%s, %s, %s, %s)
            '''
            cursor.execute(sql, ('Xinyang', 'Jiang', 'wxy.gmail.com', 3.99))

            print(f'Data inserted')
            
            # Commit transaction (save the changes)
            connection.commit()
            print(f'Data for {cursor.rowcount} students inserted and saved')

            cursor.execute('SELECT * FROM students')
            results = cursor.fetchall()
            for row in results:
                print(f'Student ID:{row['student_id']}, Name:{row['first_name']} {row['last_name']}, Email:{row['email']}, GPA:{row['gpa']}')

            # Update data
            cursor.execute('UPDATE students SET first_name = %s WHERE student_id = %s', ('Xiyang',3))
            connection.commit
            print(f'{cursor.rowcount} row(s) updated')

            # Delete data
            cursor.execute('DELETE FROM students WHERE student_id = %s', (3))
            connection.commit()
            print(f'{cursor.rowcount} row(s) deleted')

            cursor.execute('SELECT * FROM students')
            results = cursor.fetchall()
            for row in results:
                print(f'Student ID:{row['student_id']}, Name:{row['first_name']} {row['last_name']}, Email:{row['email']}, GPA:{row['gpa']}')


    finally:
        # Close the connection to free up resources
        connection.close()
        print(f'Connection closed')

except Exception as e:
    print(f'Connection Failed')
    print(f'Error:{e}')