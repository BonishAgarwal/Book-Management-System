from flask import Blueprint, request, jsonify, abort
from app import db
from app.models import Book, Review
from app.utils.db_utils import db_session
from sqlalchemy import func

# Define a blueprint for book-related routes
bp = Blueprint('book_routes', __name__)

# Route to add a new book (POST /books)
@bp.route('/books', methods=['POST'])
async def add_book():
    data = request.get_json()

    if not data or 'title' not in data or 'author' not in data:
        abort(400, description="Missing required fields: title, author")
    
    new_book = Book(
        title=data['title'],
        author=data['author'],
        genre=data.get('genre'),
        year_published=data.get('year_published'),
        summary=data.get('summary')
    )
    async with db_session() as session:
        session.add(new_book)
        await session.commit()
    
    return jsonify({"message": "Book added successfully", "book_id": new_book.id}), 201

# Route to get all books (GET /books)
@bp.route('/books', methods=['GET'])
async def get_books():
    async with db_session() as session:
        books = await session.execute(db.select(Book))
        books_list = books.scalars().all()
        
        return jsonify([{
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "year_published": book.year_published,
            "summary": book.summary
        } for book in books_list])
    
# Route to get a book by ID (GET /books/<id>)
@bp.route('/books/<int:id>', methods=['GET'])
async def get_book(id):
    async with db_session() as session:
        book = await session.execute(db.select(Book).filter_by(id=id))
        book = book.scalars().first()
        
        if not book:
            abort(404, description="Book not found")
        
        return jsonify({
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "year_published": book.year_published,
            "summary": book.summary
        })

# Route to update a book by ID (PUT /books/<id>)
@bp.route('/books/<int:id>', methods=['PUT'])
async def update_book(id):
    data = request.get_json()
    
    async with db_session() as session:
        book = await session.execute(db.select(Book).filter_by(id=id))
        book = book.scalars().first()

        if not book:
            abort(404, description="Book not found")
        
        book.title = data.get('title', book.title)
        book.author = data.get('author', book.author)
        book.genre = data.get('genre', book.genre)
        book.year_published = data.get('year_published', book.year_published)
        book.summary = data.get('summary', book.summary)
        
        await session.commit()
        
        return jsonify({"message": "Book updated successfully"}), 200

# Route to delete a book by ID (DELETE /books/<id>)
@bp.route('/books/<int:id>', methods=['DELETE'])
async def delete_book(id):
    async with db_session() as session:
        book = await session.execute(db.select(Book).filter_by(id=id))
        book = book.scalars().first()
        
        if not book:
            abort(404, description="Book not found")
        
        session.delete(book)
        await session.commit()
        
        return jsonify({"message": "Book deleted successfully"})

# Route to get summary for a book by ID (GET /books/<id>/summary)
@bp.route('/books/<int:id>/summary', methods=['GET'])
async def get_book_summary(id):
    async with db_session() as session:
        book = await session.execute(db.select(Book).filter_by(id=id))
        book = book.scalars().first()
        
        # Calculate the average rating
        avg_rating_result = await session.execute(
            db.select(func.avg(Review.rating)).filter_by(book_id=book.id)
        )
        avg_rating = avg_rating_result.scalar()  # Get the average rating
        
        if not book:
            abort(404, description="Book not found")
        
        return jsonify({"summary": book.summary, "avg_rating": avg_rating})