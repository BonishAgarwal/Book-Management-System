from flask import Blueprint, request, jsonify, abort
from app.services.llama_service import generate_summary
from app.utils.db_utils import db_session
from app import db
from app.models import Book
from app.utils.decorators.auth import authenticate

# Define a blueprint for book-summary-related routes
bp = Blueprint('generate_summary', __name__)

@authenticate
@bp.route("/books/<int:book_id>/generate-summary", methods=['POST'])
async def generate_book_summary(book_id):
    """
    Generate a summary for a book by ID
    ---
    security:
      - BasicAuth: []  # Requires Basic Authentication
    parameters:
      - name: book_id
        in: path
        type: integer
        required: true
        description: The ID of the book for which to generate the summary.
        example: 1
      - in: body
        name: content
        required: true
        description: JSON object containing the content to summarize.
        schema:
          type: object
          properties:
            content:
              type: string
              description: The content to be summarized.
              example: "This book provides an in-depth look at..."
    responses:
      200:
        description: Summary generated successfully
        schema:
          type: object
          properties:
            summary:
              type: string
              description: The generated summary of the book.
              example: "A brief overview of the book's main themes."
      400:
        description: Missing required field
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Missing required field: content"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "An error occurred while generating the summary."
    """
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


