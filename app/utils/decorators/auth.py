from functools import wraps
from flask import request, abort

# Sample credentials
USERNAME = "admin"
PASSWORD = "admin" 

def authenticate(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check for the Authorization header
        auth = request.authorization

        if not auth or auth.username != USERNAME or auth.password != PASSWORD:
            # If authentication fails, respond with 401 Unauthorized
            abort(401, description="Authentication is required.")
        return f(*args, **kwargs)
    return decorated