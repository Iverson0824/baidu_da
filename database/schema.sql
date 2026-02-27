CREATE DATABASE IF NOT EXISTS practice_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE practice_db;

DROP TABLE IF EXISTS students;

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
) ENGINE = InnoDB;

describe students;

INSERT INTO
    students (
        first_name,
        last_name,
        email,
        gpa
    )
VALUES (
        'Iverson',
        'Chen',
        'iverson3chenai@icloud.com',
        4.00
    ),
    (
        'Rebecca',
        'Zhang',
        'zhangyuhan1202@gmail.com',
        3.99
    );

START TRANSACTION;

UPDATE students SET gpa = 4 where student_id = 2;

DELETE FROM students WHERE email = 'zhangyuhan1202@gmail.com';

SELECT * FROM students;

COMMIT;

DROP TABLE IF EXISTS baidu_hot_search;

CREATE TABLE IF NOT EXISTS baidu_hot_search (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rank_index INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    hot_index INT DEFAULT 0,
    link TEXT,
    created_at DATE NOT NULL,
    UNIQUE KEY `unique_title_day` (title, created_at)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;