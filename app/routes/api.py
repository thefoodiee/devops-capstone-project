from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, session
from sqlalchemy import text, or_
from app.models import db, User, Note
from app.auth import login_required, get_current_user
from app.config import Config

api_bp = Blueprint("api", __name__)

@api_bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint for Docker & Kubernetes probes."""
    db_status = "connected"
    status_code = 200
    try:
        db.session.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
        status_code = 503

    return jsonify({
        "status": "healthy" if status_code == 200 else "degraded",
        "database": db_status,
        "version": Config.APP_VERSION,
        "environment": Config.ENV,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), status_code

@api_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not username or len(username) < 3:
        return jsonify({"success": False, "error": "Username must be at least 3 characters"}), 400
    if not email or "@" not in email:
        return jsonify({"success": False, "error": "Valid email is required"}), 400
    if not password or len(password) < 6:
        return jsonify({"success": False, "error": "Password must be at least 6 characters"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"success": False, "error": "Username already taken"}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "error": "Email already registered"}), 409

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id
    return jsonify({
        "success": True,
        "message": "User registered successfully",
        "user": user.to_dict()
    }), 201

@api_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"success": False, "error": "Invalid username or password"}), 401

    session["user_id"] = user.id
    return jsonify({
        "success": True,
        "message": "Login successful",
        "user": user.to_dict()
    }), 200

@api_bp.route("/auth/logout", methods=["POST", "GET"])
def logout():
    session.pop("user_id", None)
    return jsonify({"success": True, "message": "Logged out successfully"}), 200

@api_bp.route("/notes", methods=["GET"])
@login_required
def list_notes():
    user = get_current_user()
    query = Note.query.filter_by(user_id=user.id)

    search = request.args.get("search", "").strip()
    if search:
        query = query.filter(or_(Note.title.ilike(f"%{search}%"), Note.content.ilike(f"%{search}%")))

    category = request.args.get("category", "").strip()
    if category and category.lower() != "all":
        query = query.filter_by(category=category)

    pinned = request.args.get("pinned")
    if pinned is not None:
        is_pinned = pinned.lower() in ("true", "1")
        query = query.filter_by(is_pinned=is_pinned)

    # Return pinned notes first, then latest created
    notes = query.order_by(Note.is_pinned.desc(), Note.updated_at.desc()).all()
    return jsonify({
        "success": True,
        "count": len(notes),
        "notes": [n.to_dict() for n in notes]
    }), 200

@api_bp.route("/notes", methods=["POST"])
@login_required
def create_note():
    user = get_current_user()
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()
    category = data.get("category", "General").strip() or "General"
    is_pinned = bool(data.get("is_pinned", False))

    if not title:
        return jsonify({"success": False, "error": "Note title is required"}), 400
    if not content:
        return jsonify({"success": False, "error": "Note content is required"}), 400

    note = Note(
        user_id=user.id,
        title=title,
        content=content,
        category=category,
        is_pinned=is_pinned
    )
    db.session.add(note)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Note created successfully",
        "note": note.to_dict()
    }), 201

@api_bp.route("/notes/<int:note_id>", methods=["GET"])
@login_required
def get_note(note_id):
    user = get_current_user()
    note = Note.query.filter_by(id=note_id, user_id=user.id).first()
    if not note:
        return jsonify({"success": False, "error": "Note not found"}), 404
    return jsonify({"success": True, "note": note.to_dict()}), 200

@api_bp.route("/notes/<int:note_id>", methods=["PUT", "PATCH"])
@login_required
def update_note(note_id):
    user = get_current_user()
    note = Note.query.filter_by(id=note_id, user_id=user.id).first()
    if not note:
        return jsonify({"success": False, "error": "Note not found"}), 404

    data = request.get_json() or {}
    if "title" in data:
        title = data["title"].strip()
        if not title:
            return jsonify({"success": False, "error": "Title cannot be empty"}), 400
        note.title = title

    if "content" in data:
        content = data["content"].strip()
        if not content:
            return jsonify({"success": False, "error": "Content cannot be empty"}), 400
        note.content = content

    if "category" in data:
        note.category = data["category"].strip() or "General"

    if "is_pinned" in data:
        note.is_pinned = bool(data["is_pinned"])

    note.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Note updated successfully",
        "note": note.to_dict()
    }), 200

@api_bp.route("/notes/<int:note_id>", methods=["DELETE"])
@login_required
def delete_note(note_id):
    user = get_current_user()
    note = Note.query.filter_by(id=note_id, user_id=user.id).first()
    if not note:
        return jsonify({"success": False, "error": "Note not found"}), 404

    db.session.delete(note)
    db.session.commit()
    return jsonify({"success": True, "message": "Note deleted successfully"}), 200

@api_bp.route("/notes/<int:note_id>/pin", methods=["POST"])
@login_required
def toggle_pin_note(note_id):
    user = get_current_user()
    note = Note.query.filter_by(id=note_id, user_id=user.id).first()
    if not note:
        return jsonify({"success": False, "error": "Note not found"}), 404

    note.is_pinned = not note.is_pinned
    note.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({
        "success": True,
        "is_pinned": note.is_pinned,
        "message": f"Note {'pinned' if note.is_pinned else 'unpinned'}"
    }), 200

@api_bp.route("/stats", methods=["GET"])
@login_required
def get_stats():
    user = get_current_user()
    total_notes = Note.query.filter_by(user_id=user.id).count()
    pinned_notes = Note.query.filter_by(user_id=user.id, is_pinned=True).count()
    categories = db.session.query(Note.category, db.func.count(Note.id))\
        .filter_by(user_id=user.id).group_by(Note.category).all()

    return jsonify({
        "success": True,
        "total_notes": total_notes,
        "pinned_notes": pinned_notes,
        "categories": {cat: count for cat, count in categories}
    }), 200
