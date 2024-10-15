from flask import Blueprint, request, jsonify, abort
from app.services.llama_service import generate_summary
from app.utils.db_utils import db_session
from app import db
from app.models import Book
from app.utils.decorators.auth import authenticate

# Define a blueprint for book-summary-related routes
bp = Blueprint('generate_summary', __name__)

@bp.route("/books/<int:book_id>/generate-summary", methods=['POST'])
@authenticate
async def generate_book_summary(book_id):
    data = request.get_json()
    
    # Validate incoming data (you can improve this with Pydantic later)
    if not data or 'content' not in data:
        abort(400, description="Missing required field: content")

    book_content = data['content']

    try:
        # Call the Llama model to generate summary
        summary = await generate_summary(book_content)

        # Save the summary to the database
        async with db_session() as session:
            book = await session.execute(db.select(Book).filter_by(id=book_id)).scalar()
            
            book.summary = summary
            await session.commit()
        
        return jsonify({"summary": summary}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


