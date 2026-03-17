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

DROP TABLE IF EXISTS douban_top250;

CREATE TABLE IF NOT EXISTS douban_top250 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rank_idx INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    rating DECIMAL(2, 1) NOT NULL,
    rating_count INT DEFAULT 0,
    quote VARCHAR(500),
    link VARCHAR(500) NOT NULL,
    director VARCHAR(200),
    year SMALLINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_rank (rank_idx)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

drop table if exists movie_genres;

CREATE TABLE IF NOT EXISTS movie_genres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id INT NOT NULL,
    genre VARCHAR(50) NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES douban_top250 (id) ON DELETE CASCADE,
    UNIQUE KEY unique_movie_genre (movie_id, genre)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

drop table if exists movie_countries;

CREATE TABLE IF NOT EXISTS movie_countries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id INT NOT NULL,
    country VARCHAR(100) NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES douban_top250 (id) ON DELETE CASCADE,
    UNIQUE KEY unique_movie_country (movie_id, country)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

DROP TABLE IF EXISTS movie_cast;

CREATE TABLE IF NOT EXISTS movie_cast (
    id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id INT NOT NULL,
    actor_name VARCHAR(200) NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES douban_top250 (id) ON DELETE CASCADE,
    UNIQUE KEY unique_movie_actor (movie_id, actor_name)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;