CREATE TABLE books(
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    author VARCHAR(255),
    genre VARCHAR(255),
    year_published INT,
    summary TEXT
);

CREATE TABLE reviews(
    id SERIAL PRIMARY KEY,
    book_id INT REFERENCES books(id),
    review_text VARCHAR(255),
    rating INT
);