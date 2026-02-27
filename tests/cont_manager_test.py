from utils.mysql_helper import MysqlHelper
import time

db = MysqlHelper()

def test_transaction_safety():
    print(f'Starting transaction')
    
    # clean/prepare table
    db.execute_sql('DROP TABLE IF EXISTS students;')
    db.execute_sql('''
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
    print(f'Table ready')

    # Try broken transaction
    try:
        with db.transaction() as cursor:
            cursor.execute('INSERT INTO students VALUES(1, "Alice", "W", "alice@test.com", "2022-01-01", 4.00, CURRENT_TIMESTAMP);')
            print(f'inserted Alice (Step 1/2)')

            cursor.execute('INSERT INTO students VALUES(1, "Bob", "W", "bob@test.com", "2022-01-01", 4.00, CURRENT_TIMESTAMP);')
            print(f'inserted Bob (Step 2/2)')
    
    except Exception as e:
        print(f'Error caught locally in script: {e}')

    final_data = db.select_all('SELECT * FROM students;')

    if len(final_data) == 0:
        print(f'Transaction failed as expected')
    else:
        print(f'Failed: Alice still in DB: {final_data}')
    
test_transaction_safety()