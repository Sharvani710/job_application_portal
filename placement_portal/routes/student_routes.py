from datetime import date
from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from models import Application, Company, PlacementDrive


student_bp = Blueprint("student", __name__, url_prefix="/student")


def student_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user.role != "student":
            abort(403)
        if current_user.is_blacklisted:
            abort(403)
        return view_func(*args, **kwargs)

    return wrapped


@student_bp.route("/dashboard")
@student_required
def dashboard():
    available_companies = Company.query.filter(
        Company.approval_status == "Approved",
        Company.is_blacklisted.is_(False),
    ).order_by(Company.company_name.asc()).all()

    applied_drives = Application.query.filter_by(student_id=current_user.id).all()

    return render_template(
        "student/dashboard.html",
        available_companies=available_companies,
        applied_drives=applied_drives,
    )


@student_bp.route("/company/<int:company_id>/drives")
@student_required
def company_drives(company_id: int):
    company = Company.query.get_or_404(company_id)
    if company.approval_status != "Approved" or company.is_blacklisted:
        abort(404)

    drives = PlacementDrive.query.filter_by(
        company_id=company.id,
        status="Approved",
    ).order_by(PlacementDrive.application_deadline.asc()).all()

    return render_template(
        "student/company_drives.html",
        company=company,
        drives=drives,
    )


@student_bp.route("/drive/<int:drive_id>")
@student_required
def drive_details(drive_id: int):
    drive = PlacementDrive.query.get_or_404(drive_id)
    if (
        drive.status != "Approved"
        or drive.company.approval_status != "Approved"
        or drive.company.is_blacklisted
    ):
        abort(404)

    already_applied = Application.query.filter_by(
        student_id=current_user.id,
        drive_id=drive_id,
    ).first()

    return render_template(
        "student/drive_details.html",
        drive=drive,
        already_applied=already_applied,
    )


@student_bp.route("/drive/<int:drive_id>/apply", methods=["POST"])
@student_required
def apply_drive(drive_id: int):
    drive = PlacementDrive.query.get_or_404(drive_id)

    if (
        drive.status != "Approved"
        or drive.company.approval_status != "Approved"
        or drive.company.is_blacklisted
    ):
        abort(404)

    if drive.application_deadline < date.today():
        flash("Application deadline has passed.", "warning")
        return redirect(url_for("student.drive_details", drive_id=drive.id))

    existing_application = Application.query.filter_by(
        student_id=current_user.id,
        drive_id=drive.id,
    ).first()
    if existing_application:
        flash("You have already applied for this drive.", "info")
        return redirect(url_for("student.drive_details", drive_id=drive.id))

    application = Application(
        student_id=current_user.id,
        drive_id=drive.id,
        status="Applied",
    )
    db.session.add(application)
    db.session.commit()
    flash("Application submitted successfully.", "success")
    return redirect(url_for("student.dashboard"))


@student_bp.route("/applications/history")
@student_required
def application_history():
    applications = Application.query.filter_by(student_id=current_user.id).all()
    return render_template("student/application_history.html", applications=applications)


@student_bp.route("/profile/edit", methods=["GET", "POST"])
@student_required
def edit_profile():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        department = request.form.get("department", "").strip()
        resume = request.form.get("resume", "").strip()

        if not name or not department:
            flash("Name and department are required.", "warning")
            return redirect(url_for("student.edit_profile"))

        current_user.name = name
        current_user.department = department
        current_user.resume = resume
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("student.dashboard"))

    return render_template("student/edit_profile.html")
