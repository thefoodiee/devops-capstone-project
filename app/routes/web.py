from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy import or_
from app.models import db, User, Note
from app.auth import login_required, get_current_user

web_bp = Blueprint("web", __name__)

@web_bp.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("web.dashboard"))
    return redirect(url_for("web.login_view"))

@web_bp.route("/login", methods=["GET", "POST"])
def login_view():
    if session.get("user_id"):
        return redirect(url_for("web.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            flash("Welcome back!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("web.dashboard"))
        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html")

@web_bp.route("/register", methods=["GET", "POST"])
def register_view():
    if session.get("user_id"):
        return redirect(url_for("web.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if len(username) < 3:
            flash("Username must be at least 3 characters", "warning")
        elif "@" not in email:
            flash("Please enter a valid email address", "warning")
        elif len(password) < 6:
            flash("Password must be at least 6 characters", "warning")
        elif password != confirm_password:
            flash("Passwords do not match", "danger")
        elif User.query.filter_by(username=username).first():
            flash("Username already exists", "danger")
        elif User.query.filter_by(email=email).first():
            flash("Email already registered", "danger")
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            flash("Account created successfully! Welcome to Cloud Notes.", "success")
            return redirect(url_for("web.dashboard"))

    return render_template("register.html")

@web_bp.route("/logout")
def logout_view():
    session.pop("user_id", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("web.login_view"))

@web_bp.route("/dashboard")
@login_required
def dashboard():
    user = get_current_user()
    query = Note.query.filter_by(user_id=user.id)

    search = request.args.get("search", "").strip()
    if search:
        query = query.filter(or_(Note.title.ilike(f"%{search}%"), Note.content.ilike(f"%{search}%")))

    selected_category = request.args.get("category", "").strip()
    if selected_category and selected_category.lower() != "all":
        query = query.filter_by(category=selected_category)

    # Notes partitioned by pinned and regular
    all_notes = query.order_by(Note.is_pinned.desc(), Note.updated_at.desc()).all()
    pinned_notes = [n for n in all_notes if n.is_pinned]
    other_notes = [n for n in all_notes if not n.is_pinned]

    # Categories list for filter badges
    user_categories = [c[0] for c in db.session.query(Note.category).filter_by(user_id=user.id).distinct().all() if c[0]]

    stats = {
        "total": len(all_notes),
        "pinned": len(pinned_notes),
        "categories_count": len(user_categories)
    }

    return render_template(
        "dashboard.html",
        user=user,
        pinned_notes=pinned_notes,
        other_notes=other_notes,
        categories=user_categories,
        selected_category=selected_category,
        search=search,
        stats=stats
    )

@web_bp.route("/notes/create", methods=["POST"])
@login_required
def create_note():
    user = get_current_user()
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    category = request.form.get("category", "General").strip() or "General"
    is_pinned = bool(request.form.get("is_pinned"))

    if not title or not content:
        flash("Title and Content are required to create a note", "warning")
    else:
        note = Note(
            user_id=user.id,
            title=title,
            content=content,
            category=category,
            is_pinned=is_pinned
        )
        db.session.add(note)
        db.session.commit()
        flash("Note created successfully!", "success")

    return redirect(url_for("web.dashboard"))

@web_bp.route("/notes/<int:note_id>/edit", methods=["POST"])
@login_required
def edit_note(note_id):
    user = get_current_user()
    note = Note.query.filter_by(id=note_id, user_id=user.id).first()
    if not note:
        flash("Note not found", "danger")
        return redirect(url_for("web.dashboard"))

    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    category = request.form.get("category", "General").strip() or "General"
    is_pinned = bool(request.form.get("is_pinned"))

    if not title or not content:
        flash("Title and Content cannot be empty", "warning")
    else:
        note.title = title
        note.content = content
        note.category = category
        note.is_pinned = is_pinned
        note.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        flash("Note updated successfully!", "success")

    return redirect(url_for("web.dashboard"))

@web_bp.route("/notes/<int:note_id>/delete", methods=["POST"])
@login_required
def delete_note(note_id):
    user = get_current_user()
    note = Note.query.filter_by(id=note_id, user_id=user.id).first()
    if note:
        db.session.delete(note)
        db.session.commit()
        flash("Note deleted successfully!", "info")
    else:
        flash("Note not found", "danger")

    return redirect(url_for("web.dashboard"))

@web_bp.route("/notes/<int:note_id>/pin", methods=["POST"])
@login_required
def pin_note(note_id):
    user = get_current_user()
    note = Note.query.filter_by(id=note_id, user_id=user.id).first()
    if note:
        note.is_pinned = not note.is_pinned
        note.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        state = "pinned" if note.is_pinned else "unpinned"
        flash(f"Note {state} successfully!", "info")

    return redirect(url_for("web.dashboard"))
