from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from extensions import db
from models import Admin, Company, Student


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        if current_user.role == "company":
            return redirect(url_for("company.dashboard"))
        return redirect(url_for("student.dashboard"))

    if request.method == "POST":
        selected_role = request.form.get("role", "").strip().lower()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if selected_role in ("", "admin"):
            user = Admin.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for("admin.dashboard"))

        if selected_role in ("", "company"):
            company = Company.query.filter_by(email=username).first()
            if company and company.check_password(password):
                if company.approval_status != "Approved":
                    flash("Company account is pending admin approval.", "warning")
                    return redirect(url_for("auth.login"))
                if company.is_blacklisted:
                    flash("Company is blacklisted.", "danger")
                    return redirect(url_for("auth.login"))

                login_user(company)
                return redirect(url_for("company.dashboard"))

        if selected_role in ("", "student"):
            student = Student.query.filter_by(email=username).first()
            if student and student.check_password(password):
                if student.is_blacklisted:
                    flash("Student account is blacklisted.", "danger")
                    return redirect(url_for("auth.login"))

                login_user(student)
                return redirect(url_for("student.dashboard"))

        flash("Invalid credentials.", "danger")

    return render_template("login.html")


@auth_bp.route("/register/student", methods=["GET", "POST"])
def register_student():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        department = request.form.get("department", "").strip()
        password = request.form.get("password", "")
        resume = request.form.get("resume", "").strip()

        if Student.query.filter_by(email=email).first():
            flash("Student email already registered.", "warning")
            return redirect(url_for("auth.register_student"))

        student = Student(
            name=name,
            email=email,
            department=department,
            resume=resume,
        )
        student.set_password(password)

        db.session.add(student)
        db.session.commit()
        flash("Student registered successfully. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register_student.html")


@auth_bp.route("/register/company", methods=["GET", "POST"])
def register_company():
    if request.method == "POST":
        company_name = request.form.get("company_name", "").strip()
        hr_contact = request.form.get("hr_contact", "").strip()
        website = request.form.get("website", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if Company.query.filter_by(email=email).first():
            flash("Company email already registered.", "warning")
            return redirect(url_for("auth.register_company"))

        company = Company(
            company_name=company_name,
            hr_contact=hr_contact,
            website=website,
            email=email,
            approval_status="Pending",
        )
        company.set_password(password)

        db.session.add(company)
        db.session.commit()
        flash("Company registered and waiting for admin approval.", "info")
        return redirect(url_for("auth.login"))

    return render_template("register_company.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "success")
    return redirect(url_for("index"))
