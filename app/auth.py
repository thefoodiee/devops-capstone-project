from functools import wraps
from flask import session, redirect, url_for, request, jsonify
from app.models import db, User

def login_required(f):
    """Decorator to require login for web routes or API endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Check Flask session
        user_id = session.get("user_id")
        if user_id:
            user = db.session.get(User, user_id)
            if user:
                return f(*args, **kwargs)

        # 2. Check API Basic Auth or Header for API requests
        auth = request.authorization
        if auth and auth.username and auth.password:
            user = User.query.filter_by(username=auth.username).first()
            if user and user.check_password(auth.password):
                session["user_id"] = user.id
                return f(*args, **kwargs)

        # If it's an API request, return 401 JSON
        if request.path.startswith("/api/"):
            return jsonify({
                "success": False,
                "error": "Authentication required. Please provide valid session or credentials."
            }), 401

        # Otherwise redirect to login page
        return redirect(url_for("web.login_view", next=request.url))

    return decorated_function

def get_current_user():
    """Retrieve current logged-in user object or None."""
    user_id = session.get("user_id")
    if user_id:
        return db.session.get(User, user_id)
    return None
