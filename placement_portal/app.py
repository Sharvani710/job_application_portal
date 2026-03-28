from flask import Flask, redirect, render_template, url_for
from flask_login import current_user

from config import Config
from extensions import db, login_manager
from models import Admin, Company, Student
from routes.admin_routes import admin_bp
from routes.auth_routes import auth_bp
from routes.company_routes import company_bp
from routes.student_routes import student_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)

    @app.route("/")
    def index():
        if not current_user.is_authenticated:
            return render_template("home.html")

        if current_user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        if current_user.role == "company":
            return redirect(url_for("company.dashboard"))
        return redirect(url_for("student.dashboard"))

    with app.app_context():
        db.create_all()
        ensure_default_admin()

    return app


@login_manager.user_loader
def load_user(user_id: str):
    try:
        role, raw_id = user_id.split("-", 1)
        entity_id = int(raw_id)
    except (ValueError, AttributeError):
        return None

    if role == "admin":
        return Admin.query.get(entity_id)
    if role == "student":
        return Student.query.get(entity_id)
    if role == "company":
        return Company.query.get(entity_id)
    return None


def ensure_default_admin() -> None:
    admin = Admin.query.filter_by(username="admin").first()
    if admin:
        return

    admin = Admin(username="admin")
    admin.set_password("admin123")
    db.session.add(admin)
    db.session.commit()


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
