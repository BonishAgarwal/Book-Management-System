# Book Management System

## Overview

The Book Management System is a Flask-based web application that allows users to manage a collection of books. Users can add, update, delete, and retrieve books, along with their summaries and reviews. This application utilizes PostgreSQL for data storage and provides a simple RESTful API for interaction.

## Features

- **Add a New Book**: Add books with details such as title, author, genre, year published, and summary.
- **Retrieve All Books**: Fetch a list of all books in the database.
- **Retrieve a Book by ID**: Get detailed information about a specific book.
- **Update a Book**: Modify the details of an existing book.
- **Delete a Book**: Remove a book from the database.
- **Get Book Summary**: Fetch a book's summary and average rating.
- **Add Reviews**: Add reviews and ratings for each book.
- **Get Reviews**: Get all reviews of a book

## Tech Stack

- **Backend**: Flask
- **Database**: PostgreSQL
- **Asynchronous Support**: SQLAlchemy with AsyncIO
- **API Documentation**: Swagger UI via Flasgger

## Installation

### Prerequisites

- Python 3.7 or higher
- PostgreSQL
- pip (Python package manager)

### Steps to Set Up the Application

1. **Clone the repository:**

   ```bash
   git clone https://github.com/BonishAgarwal/Book-Management-System.git
   cd Book-Management-System

2. **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # For Windows use: venv\Scripts\activate

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt

4. **Set up the PostgreSQL database**
    ```sql
    CREATE DATABASE book_management_system;

5. **Run the application**
    ```bash
    flask run


## CI/CD Workflow for Deploying the Book Management System on AWS

### Prerequisites

1.	AWS Account: Make sure you have an AWS account set up.
2.	IAM User: Create an IAM user with permissions to deploy to AWS services (like EC2, RDS, etc.) and generate access keys for this user.
3.	EC2 Instance: Set up an EC2 instance where you will deploy your application.
4.	PostgreSQL Database: Set up a PostgreSQL database on AWS RDS (or any other cloud database service).
5.	GitHub Repository: Your application code should be stored in a GitHub repository.

### Steps to Set Up CI/CD Workflow

1. Create a Dockerfile
2. Create a GitHub Actions Workflow: In your GitHub repository, create a new directory .github/workflows and add a YAML file (e.g., bms.yml). This file will define the CI/CD workflow.
3. Deploying the Application: When we push changes to the main branch of your GitHub repository, GitHub Actions will automatically run the CI/CD workflow defined in .github/workflows/bms.yml.README.md

