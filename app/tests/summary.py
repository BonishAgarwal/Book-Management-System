import unittest
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from flask import Flask, json
from app import create_app
from app.models import Book
from app.routes.book_routes import bp
from app.utils.db_utils import db_session

class AddSummaryTestCase(unittest.TestCase):
    def setUp(self):
        """Set up the test client."""
        self.app = create_app()
        self.app.register_blueprint(bp, name='generate_summary_test')
        self.client = self.app.test_client()
        self.app.testing = True  # Set Flask to testing mode

    @pytest.mark.asyncio
    @patch('app.routes.generate_summary', new_callable=AsyncMock)
    @patch('app.utils.db_utils.db_session', new_callable=AsyncMock)
    async def test_generate_book_summary_success(mock_db_session, mock_generate_summary, client):
        """Test generating a book summary successfully."""

        # Mock session
        mock_session = AsyncMock()
        mock_db_session.return_value.__aenter__.return_value = mock_session

        # Mock existing book
        mock_book = Book(id=1, title="Test Book", author="Test Author", genre="Fiction", year_published=2020, summary="Old Summary")
        mock_session.execute.return_value.scalar.return_value = mock_book

        # Mock the summary generation response
        mock_generate_summary.return_value = "Generated Summary"

        # Make the POST request to generate the summary
        request_data = {'content': 'Book content to generate summary'}
        response = await client.post('/books/1/generate-summary', data=json.dumps(request_data), content_type='application/json')

        # Assert status code and response content
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["summary"] == "Generated Summary"

        # Ensure the summary was saved to the book
        assert mock_book.summary == "Generated Summary"

        # Ensure commit was called once
        mock_session.commit.assert_called_once()


    @pytest.mark.asyncio
    @patch('app.routes.generate_summary', new_callable=AsyncMock)
    @patch('app.utils.db_utils.db_session', new_callable=AsyncMock)
    async def test_generate_book_summary_missing_content(mock_db_session, mock_generate_summary, client):
        """Test generating a book summary fails when 'content' is missing."""
        
        # Make the POST request with missing 'content' field
        request_data = {}
        response = await client.post('/books/1/generate-summary', data=json.dumps(request_data), content_type='application/json')

        # Assert status code and error message
        assert response.status_code == 400
        assert "Missing required field: content" in response.get_data(as_text=True)

        # Ensure the external summary generator and commit were not called
        mock_generate_summary.assert_not_called()


    @pytest.mark.asyncio
    @patch('app.routes.generate_summary', new_callable=AsyncMock)
    @patch('app.utils.db_utils.db_session', new_callable=AsyncMock)
    async def test_generate_book_summary_book_not_found(mock_db_session, mock_generate_summary, client):
        """Test generating a summary when the book is not found."""
        
        # Mock session
        mock_session = AsyncMock()
        mock_db_session.return_value.__aenter__.return_value = mock_session

        # Simulate the case where the book is not found
        mock_session.execute.return_value.scalar.return_value = None

        # Make the POST request with valid content
        request_data = {'content': 'Book content to generate summary'}
        response = await client.post('/books/999/generate-summary', data=json.dumps(request_data), content_type='application/json')

        # Assert status code and error message
        assert response.status_code == 404
        assert "Book not found" in response.get_data(as_text=True)

        # Ensure the external summary generator and commit were not called
        mock_generate_summary.assert_not_called()
        mock_session.commit.assert_not_called()


    @pytest.mark.asyncio
    @patch('app.routes.generate_summary', new_callable=AsyncMock)
    @patch('app.utils.db_utils.db_session', new_callable=AsyncMock)
    async def test_generate_book_summary_external_service_error(mock_db_session, mock_generate_summary, client):
        """Test generating a summary when the external service fails."""

        # Mock session
        mock_session = AsyncMock()
        mock_db_session.return_value.__aenter__.return_value = mock_session

        # Mock existing book
        mock_book = Book(id=1, title="Test Book", author="Test Author", genre="Fiction", year_published=2020, summary="Old Summary")
        mock_session.execute.return_value.scalar.return_value = mock_book

        # Mock the external service throwing an exception
        mock_generate_summary.side_effect = Exception("External service error")

        # Make the POST request with valid content
        request_data = {'content': 'Book content to generate summary'}
        response = await client.post('/books/1/generate-summary', data=json.dumps(request_data), content_type='application/json')

        # Assert status code and error message
        assert response.status_code == 500
        assert "External service error" in response.get_data(as_text=True)

        # Ensure commit was not called due to failure
        mock_session.commit.assert_not_called()