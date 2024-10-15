from flask import Blueprint, request, jsonify, abort
from app import db
from app.models import Book, Review
from app.utils.db_utils import db_session
from sqlalchemy import func
from flasgger.utils import swag_from
from app.utils.decorators.auth import authenticate

# Define a blueprint for book-related routes
bp = Blueprint('book_routes', __name__)

# Route to add a new book (POST /books)
@authenticate
@bp.route('/books', methods=['POST'])
async def add_book():
    """
    Add a new book
    ---
    security:
      - BasicAuth: []  # Requires Basic Authentication
    parameters:
      - name: book
        in: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              description: The title of the book.
              example: "The Great Gatsby"
            author:
              type: string
              description: The author of the book.
              example: "F. Scott Fitzgerald"
            genre:
              type: string
              description: The genre of the book.
              example: "Fiction"
            year_published:
              type: integer
              description: The year the book was published.
              example: 1925
            summary:
              type: string
              description: A brief summary of the book.
              example: "A novel set in the 1920s."
    responses:
      201:
        description: Book added successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Book added successfully"
            book_id:
              type: integer
              example: 1
      400:
        description: Missing required fields
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Missing required fields: title, author"
      500:
        description: Internal server error
    """
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
@authenticate
@bp.route('/books', methods=['GET'])
async def get_books():
    """
    Retrieve all books
    ---
    security:
      - BasicAuth: []  # Requires Basic Authentication
    responses:
      200:
        description: A list of all books
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: The ID of the book.
                example: 1
              title:
                type: string
                description: The title of the book.
                example: "The Great Gatsby"
              author:
                type: string
                description: The author of the book.
                example: "F. Scott Fitzgerald"
              genre:
                type: string
                description: The genre of the book.
                example: "Fiction"
              year_published:
                type: integer
                description: The year the book was published.
                example: 1925
              summary:
                type: string
                description: A brief summary of the book.
                example: "A novel set in the 1920s."
      401:
        description: Unauthorized access
      500:
        description: Internal server error
    """
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
        } for book in books_list]), 200
    
# Route to get a book by ID (GET /books/<id>)
@authenticate
@bp.route('/books/<int:id>', methods=['GET'])
async def get_book(id):
    """
    Retrieve a book by ID
    ---
    security:
      - BasicAuth: []  # Requires Basic Authentication
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The ID of the book to retrieve.
        example: 1
    responses:
      200:
        description: A book object
        schema:
          type: object
          properties:
            id:
              type: integer
              description: The ID of the book.
              example: 1
            title:
              type: string
              description: The title of the book.
              example: "The Great Gatsby"
            author:
              type: string
              description: The author of the book.
              example: "F. Scott Fitzgerald"
            genre:
              type: string
              description: The genre of the book.
              example: "Fiction"
            year_published:
              type: integer
              description: The year the book was published.
              example: 1925
            summary:
              type: string
              description: A brief summary of the book.
              example: "A novel set in the 1920s."
      404:
        description: Book not found
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Book not found"
      401:
        description: Unauthorized access
      500:
        description: Internal server error
    """
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
        }), 200

# Route to update a book by ID (PUT /books/<id>)
@authenticate
@bp.route('/books/<int:id>', methods=['PUT'])
async def update_book(id):
    """
    Update a book by ID
    ---
    security:
      - BasicAuth: []  # Requires Basic Authentication
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The ID of the book to update.
        example: 1
      - in: body
        name: book
        required: true
        description: JSON object containing the fields to update.
        schema:
          type: object
          properties:
            title:
              type: string
              description: The title of the book.
              example: "The Great Gatsby - Updated"
            author:
              type: string
              description: The author of the book.
              example: "F. Scott Fitzgerald"
            genre:
              type: string
              description: The genre of the book.
              example: "Fiction"
            year_published:
              type: integer
              description: The year the book was published.
              example: 1925
            summary:
              type: string
              description: A brief summary of the book.
              example: "A novel set in the 1920s, updated for modern readers."
    responses:
      200:
        description: Book updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Book updated successfully"
      404:
        description: Book not found
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Book not found"
      401:
        description: Unauthorized access
      500:
        description: Internal server error
    """
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
@authenticate
@bp.route('/books/<int:id>', methods=['DELETE'])
async def delete_book(id):
    """
    Delete a book by ID
    ---
    security:
      - BasicAuth: []  # Requires Basic Authentication
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The ID of the book to delete.
        example: 1
    responses:
      200:
        description: Book deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Book deleted successfully"
      404:
        description: Book not found
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Book not found"
      401:
        description: Unauthorized access
      500:
        description: Internal server error
    """
    async with db_session() as session:
        book = await session.execute(db.select(Book).filter_by(id=id))
        book = book.scalars().first()
        
        if not book:
            abort(404, description="Book not found")
        
        session.delete(book)
        await session.commit()
        
        return jsonify({"message": "Book deleted successfully"}), 200

# Route to get summary for a book by ID (GET /books/<id>/summary)
@authenticate
@bp.route('/books/<int:id>/summary', methods=['GET'])
async def get_book_summary(id):
    """
    Retrieve a book's summary and average rating by ID
    ---
    security:
      - BasicAuth: []  # Requires Basic Authentication
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The ID of the book to retrieve the summary and average rating for.
        example: 1
    responses:
      200:
        description: A book summary and its average rating
        schema:
          type: object
          properties:
            summary:
              type: string
              description: A brief summary of the book.
              example: "A novel set in the 1920s."
            avg_rating:
              type: number
              format: float
              description: The average rating of the book.
              example: 4.5
      404:
        description: Book not found
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Book not found"
      401:
        description: Unauthorized access
      500:
        description: Internal server error
    """
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