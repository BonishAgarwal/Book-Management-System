from flask import Blueprint, request, jsonify, abort
from app import db
from app.models import Book, Review
from app.utils.db_utils import db_session

# Define a blueprint for book-related routes
bp = Blueprint('review_routes', __name__)

# Route to add review for a particular book
@bp.route('/books/<int:book_id>/reviews', methods=['POST'])
async def add_review(book_id):
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
    
    return jsonify({"message": "Review added successfully"})


# Route to get all reviews for a particular book
@bp.route("/books/<int:book_id>/reviews", methods=['GET'])
async def get_reviews(book_id):
    
   async with db_session() as session:
        reviews = await session.execute(db.select(Review).filter_by(book_id=book_id))
        reviews_list = reviews.scalars().all()
        
        return jsonify([{
            "id": review.id,
            "review_text": review.review_text,
            "rating": review.rating
        } for review in reviews_list])


