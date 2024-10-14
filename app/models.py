from flask_sqlalchemy import SQLAlchemy

# Initialize the database instance
db = SQLAlchemy()

# Book model definition
class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(100), nullable=True)
    year_published = db.Column(db.Integer, nullable=True)
    summary = db.Column(db.Text, nullable=True) 
    
    # Relationship to reviews
    reviews = db.relationship('Review', backref='book', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Book {self.title} by {self.author}>"

# Review model definition
class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    review_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    
    def __repr__(self):
        return f"<Review {self.rating}/5 for Book ID {self.book_id}>"