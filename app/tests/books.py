import unittest
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from flask import Flask, json
from app import create_app
from app.models import Book
from app.routes.book_routes import bp
from app.utils.db_utils import db_session

class AddBookTestCase(unittest.TestCase):
    def setUp(self):
        """Set up the test client."""
        self.app = create_app()
        self.app.register_blueprint(bp, name='book_routes_test')
        self.client = self.app.test_client()
        self.app.testing = True  # Set Flask to testing mode
        
    
    @pytest.mark.asyncio
    @patch('app.utils.db_utils.db_session', new_callable=AsyncMock)  # Mock the db_session to avoid database interaction
    async def test_add_book_success(self, mock_db_session):
        """Test adding a book successfully."""
        
        # Mock the database session and commit
        mock_session = AsyncMock()
        mock_db_session.return_value.__aenter__.return_value = mock_session
        
        # Define the test payload
        book_data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'genre': 'Fiction',
            'year_published': 2021,
            'summary': ''
        }
        
        # Send POST request to add the book
        response = self.client.post('/books', data=json.dumps(book_data), content_type='application/json')
        
        # Check the response
        self.assertEqual(response.status_code, 201)
        self.assertIn('Book added successfully', response.get_data(as_text=True))
        mock_session.add.assert_called_once()  # Ensure the book was added to the session
        mock_session.commit.assert_called_once()  # Ensure commit was called
    
    @pytest.mark.asyncio
    @patch('app.utils.db_utils.db_session', new_callable=AsyncMock)  # Mock the db_session for this test as well
    async def test_add_book_missing_fields(self, mock_db_session):
        """Test adding a book fails when required fields are missing."""
        
        # Define payload missing title and author
        book_data = {
            'genre': 'Fiction',
            'year_published': 2021
        }
        
        # Send POST request with missing fields
        response = self.client.post('/books', data=json.dumps(book_data), content_type='application/json')
        
        # Check for bad request response
        self.assertEqual(response.status_code, 400)
        self.assertIn('Missing required fields: title, author', response.get_data(as_text=True))
    
    @pytest.mark.asyncio
    @patch('app.utils.db_utils.db_session', new_callable=AsyncMock)  # Mock db_session
    async def test_get_books(mock_db_session, client):
        """Test fetching all books successfully."""

        # Create a mock session
        mock_session = AsyncMock()
        mock_db_session.return_value.__aenter__.return_value = mock_session
        
        # Mock book data
        mock_books = [
            Book(id=1, title="Book 1", author="Author 1", genre="Fiction", year_published=2020, summary="Summary 1"),
            Book(id=2, title="Book 2", author="Author 2", genre="Sci-Fi", year_published=2021, summary="Summary 2"),
        ]
        
        # Mock the database response
        mock_session.execute.return_value.scalars.return_value.all.return_value = mock_books

        # Make the GET request to fetch all books
        response = await client.get('/books')

        # Assert status code and check response content
        assert response.status_code == 200
        json_data = response.get_json()
        assert len(json_data) == 2
        assert json_data[0]["title"] == "Book 1"
        assert json_data[1]["title"] == "Book 2"

        # Ensure the session's execute method was called once
        mock_session.execute.assert_called_once()
    
    
    @pytest.mark.asyncio
    @patch('app.utils.db_utils.db_session', new_callable=AsyncMock)  # Mock db_session
    async def test_get_book_success(mock_db_session, client):
        """Test fetching a book by ID successfully."""

        # Create a mock session
        mock_session = AsyncMock()
        mock_db_session.return_value.__aenter__.return_value = mock_session

        # Mock a single book
        mock_book = Book(id=1, title="Book 1", author="Author 1", genre="Fiction", year_published=2020, summary="Summary 1")

        # Mock the database response
        mock_session.execute.return_value.scalars.return_value.first.return_value = mock_book

        # Make the GET request to fetch the book by ID
        response = await client.get('/books/1')

        # Assert status code and check response content
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["title"] == "Book 1"
        assert json_data["author"] == "Author 1"
        assert json_data["genre"] == "Fiction"

        # Ensure the session's execute method was called once
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.utils.db_utils.db_session', new_callable=AsyncMock)  # Mock db_session
    async def test_get_book_not_found(mock_db_session, client):
        """Test fetching a book by ID when the book is not found."""

        # Create a mock session
        mock_session = AsyncMock()
        mock_db_session.return_value.__aenter__.return_value = mock_session

        # Mock no book found
        mock_session.execute.return_value.scalars.return_value.first.return_value = None

        # Make the GET request to fetch the book by ID
        response = await client.get('/books/999')  # ID 999, assume it doesn't exist

        # Assert status code and check response content
        assert response.status_code == 404
        assert "Book not found" in response.get_data(as_text=True)

        # Ensure the session's execute method was called once
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.utils.db_utils.db_session', new_callable=AsyncMock)
    async def test_update_book_success(mock_db_session, client):
        """Test updating a book successfully."""
        
        # Mock session
        mock_session = AsyncMock()
        mock_db_session.return_value.__aenter__.return_value = mock_session

        # Mock existing book
        mock_book = Book(id=1, title="Old Title", author="Old Author", genre="Fiction", year_published=2020, summary="Old Summary")

        # Mock the database response for book retrieval
        mock_session.execute.return_value.scalars.return_value.first.return_value = mock_book

        # New book data to update
        update_data = {
            'title': 'New Title',
            'author': 'New Author',
            'genre': 'Sci-Fi',
            'year_published': 2021,
            'summary': 'New Summary'
        }

        # Make the PUT request to update the book
        response = await client.put('/books/1', data=json.dumps(update_data), content_type='application/json')

        # Assert status code and response content
        assert response.status_code == 200
        assert "Book updated successfully" in response.get_data(as_text=True)

        # Ensure the book object was updated
        assert mock_book.title == 'New Title'
        assert mock_book.author == 'New Author'
        assert mock_book.genre == 'Sci-Fi'
        assert mock_book.year_published == 2021
        assert mock_book.summary == 'New Summary'

        # Ensure commit was called once
        mock_session.commit.assert_called_once()


    @pytest.mark.asyncio
    @patch('app.utils.db_utils.db_session', new_callable=AsyncMock)
    async def test_update_book_not_found(mock_db_session, client):
        """Test updating a book that doesn't exist."""
        
        # Mock session
        mock_session = AsyncMock()
        mock_db_session.return_value.__aenter__.return_value = mock_session

        # Mock no book found
        mock_session.execute.return_value.scalars.return_value.first.return_value = None

        # Data for update (can be anything, since the book doesn't exist)
        update_data = {
            'title': 'New Title'
        }

        # Make the PUT request to update a non-existing book
        response = await client.put('/books/999', data=json.dumps(update_data), content_type='application/json')

        # Assert status code and response content
        assert response.status_code == 404
        assert "Book not found" in response.get_data(as_text=True)

        # Ensure commit was never called
        mock_session.commit.assert_not_called()
    
    @pytest.mark.asyncio
    @patch('app.utils.db_utils.db_session', new_callable=AsyncMock)
    async def test_delete_book_success(mock_db_session, client):
        """Test deleting a book successfully."""
        
        # Mock session
        mock_session = AsyncMock()
        mock_db_session.return_value.__aenter__.return_value = mock_session

        # Mock existing book
        mock_book = Book(id=1, title="Test Book", author="Test Author", genre="Fiction", year_published=2020, summary="Test Summary")

        # Mock the database response for book retrieval
        mock_session.execute.return_value.scalars.return_value.first.return_value = mock_book

        # Make the DELETE request to delete the book
        response = await client.delete('/books/1')

        # Assert status code and response content
        assert response.status_code == 200
        assert "Book deleted successfully" in response.get_data(as_text=True)

        # Ensure the book was deleted
        mock_session.delete.assert_called_once_with(mock_book)

        # Ensure commit was called once
        mock_session.commit.assert_called_once()


    @pytest.mark.asyncio
    @patch('app.utils.db_utils.db_session', new_callable=AsyncMock)
    async def test_delete_book_not_found(mock_db_session, client):
        """Test deleting a book that doesn't exist."""
        
        # Mock session
        mock_session = AsyncMock()
        mock_db_session.return_value.__aenter__.return_value = mock_session

        # Mock no book found
        mock_session.execute.return_value.scalars.return_value.first.return_value = None

        # Make the DELETE request to delete a non-existing book
        response = await client.delete('/books/999')

        # Assert status code and response content
        assert response.status_code == 404
        assert "Book not found" in response.get_data(as_text=True)

        # Ensure delete and commit were not called
        mock_session.delete.assert_not_called()
        mock_session.commit.assert_not_called()