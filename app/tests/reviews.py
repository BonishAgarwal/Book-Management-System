import unittest
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from flask import Flask, json
from app import create_app
from app.models import Review
from app.routes.review_routes import bp
from app.utils.db_utils import db_session

class AddBookTestCase(unittest.TestCase):
    def setUp(self):
        """Set up the test client."""
        self.app = create_app()
        self.app.register_blueprint(bp, name='review_routes_test')
        self.client = self.app.test_client()
        self.app.testing = True  # Set Flask to testing mode
    
    @pytest.mark.asyncio
    @patch('app.utils.db_utils.db_session', new_callable=AsyncMock)
    async def test_add_review_success(mock_db_session, client):
        """Test adding a review successfully."""
        
        # Mock session
        mock_session = AsyncMock()
        mock_db_session.return_value.__aenter__.return_value = mock_session

        # Review data to add
        review_data = {
            'review_text': 'Great book!',
            'rating': 5,
            'book_id': 1
        }

        # Make the POST request to add the review
        response = await client.post('/books/1/reviews', data=json.dumps(review_data), content_type='application/json')

        # Assert status code and response content
        assert response.status_code == 200
        assert "Review added successfully" in response.get_data(as_text=True)

        # Ensure the review was added to the session
        mock_session.add.assert_called_once()
        
        # Ensure commit was called once
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.utils.db_utils.db_session', new_callable=AsyncMock)
    async def test_add_review_missing_field(mock_db_session, client):
        """Test adding a review fails when required fields are missing."""
        
        # Mock session
        mock_session = AsyncMock()
        mock_db_session.return_value.__aenter__.return_value = mock_session

        # Review data missing 'review_text'
        review_data = {
            'rating': 5
        }

        # Make the POST request to add the review with missing fields
        response = await client.post('/books/1/reviews', data=json.dumps(review_data), content_type='application/json')

        # Assert status code and error message
        assert response.status_code == 400
        assert "Missing required field: review" in response.get_data(as_text=True)

        # Ensure add and commit were not called
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()
    
    @pytest.mark.asyncio
    @patch('app.utils.db_utils.db_session', new_callable=AsyncMock)
    async def test_get_reviews_success(mock_db_session, client):
        """Test fetching all reviews for a book successfully."""
        
        # Mock session
        mock_session = AsyncMock()
        mock_db_session.return_value.__aenter__.return_value = mock_session

        # Mock reviews data
        mock_reviews = [
            Review(id=1, review_text="Great book!", rating=5, book_id=1),
            Review(id=2, review_text="Not bad", rating=4, book_id=1)
        ]

        # Mock the database response
        mock_session.execute.return_value.scalars.return_value.all.return_value = mock_reviews

        # Make the GET request to fetch all reviews for book ID 1
        response = await client.get('/books/1/reviews')

        # Assert status code and response content
        assert response.status_code == 200
        json_data = response.get_json()
        assert len(json_data) == 2
        assert json_data[0]["review_text"] == "Great book!"
        assert json_data[1]["review_text"] == "Not bad"

        # Ensure execute was called once
        mock_session.execute.assert_called_once()


    @pytest.mark.asyncio
    @patch('app.utils.db_utils.db_session', new_callable=AsyncMock)
    async def test_get_reviews_empty(mock_db_session, client):
        """Test fetching reviews for a book with no reviews."""
        
        # Mock session
        mock_session = AsyncMock()
        mock_db_session.return_value.__aenter__.return_value = mock_session

        # Mock no reviews found
        mock_session.execute.return_value.scalars.return_value.all.return_value = []

        # Make the GET request to fetch reviews for a book with no reviews
        response = await client.get('/books/1/reviews')

        # Assert status code and response content
        assert response.status_code == 200
        json_data = response.get_json()
        assert len(json_data) == 0  # No reviews found

        # Ensure execute was called once
        mock_session.execute.assert_called_once()