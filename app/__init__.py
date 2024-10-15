from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from flasgger import Swagger

# Initialize the database instance
db = SQLAlchemy()

DATABASE_URL = 'postgresql+asyncpg://postgres:@localhost/book_management_system'
engine = create_async_engine(DATABASE_URL, echo=True)

# Create an AsyncSession
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

def create_app():
    app = Flask(__name__)

    Swagger(app)
    # Configure the app
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL # Update with your DB URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable track modifications
    
    # Initialize the database with the app
    db.init_app(app)
    
    # Set the db.session to the async sessionmaker
    db.session = scoped_session(async_session)

    # Import and register blueprints here
    from app.routes import book_routes, generate_summary, review_routes
    app.register_blueprint(book_routes.bp)
    app.register_blueprint(generate_summary.bp)
    app.register_blueprint(review_routes.bp)

    return app