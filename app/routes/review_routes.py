from flask import Blueprint, request, jsonify, abort
from app import db
from app.models import Book, Review
from app.utils.db_utils import db_session
from app.utils.decorators.auth import authenticate

# Define a blueprint for book-related routes
bp = Blueprint('review_routes', __name__)

# Route to add review for a particular book
@bp.route('/books/<int:book_id>/reviews', methods=['POST'])
@authenticate
async def add_review(book_id):
    """
    Add a review to a book
    ---
    security:
      - BasicAuth: []  # Requires Basic Authentication
    parameters:
      - name: book_id
        in: path
        type: integer
        required: true
        description: The ID of the book to add the review to.
        example: 1
      - in: body
        name: review
        required: true
        description: JSON object containing the review text and rating.
        schema:
          type: object
          properties:
            review_text:
              type: string
              description: The text of the review.
              example: "This book is fantastic!"
            rating:
              type: integer
              description: The rating for the book (1-5).
              example: 5
    responses:
      201:
        description: Review added successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Review added successfully"
      400:
        description: Missing required field (review_text or rating)
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Missing required field: review"
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
    
    if not data or 'review_text' not in data:
        abort(400, description="Missing required field: review")
    
    new_book_review = Review(
        review_text=data['review_text'],
        rating=data['rating'],
        book_id=book_id
    )
    async with db_session() as session:
        session.add(new_book_review)
        await session.commit()
    
    return jsonify({"message": "Review added successfully"}), 201


# Route to get all reviews for a particular book
@bp.route("/books/<int:book_id>/reviews", methods=['GET'])
@authenticate
async def get_reviews(book_id):
    """
    Retrieve all reviews for a specific book
    ---
    security:
      - BasicAuth: []  # Requires Basic Authentication
    parameters:
      - name: book_id
        in: path
        type: integer
        required: true
        description: The ID of the book to retrieve reviews for.
        example: 1
    responses:
      200:
        description: A list of reviews for the book
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: The ID of the review.
                example: 1
              review_text:
                type: string
                description: The text of the review.
                example: "Great book!"
              rating:
                type: integer
                description: The rating for the book (1-5).
                example: 5
      404:
        description: Book not found or no reviews available
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Book not found or no reviews available"
      401:
        description: Unauthorized access
      500:
        description: Internal server error
    """
    async with db_session() as session:
        reviews = await session.execute(db.select(Review).filter_by(book_id=book_id))
        reviews_list = reviews.scalars().all()
        
        return jsonify([{
            "id": review.id,
            "review_text": review.review_text,
            "rating": review.rating
        } for review in reviews_list]), 200


