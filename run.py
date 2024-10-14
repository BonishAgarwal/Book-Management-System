from app import create_app  # Import the create_app function

# Create the Flask app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)