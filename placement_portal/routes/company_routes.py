from datetime import datetime
from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from models import Application, PlacementDrive


company_bp = Blueprint("company", __name__, url_prefix="/company")


def company_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user.role != "company":
            abort(403)
        if current_user.approval_status != "Approved" or current_user.is_blacklisted:
            abort(403)
        return view_func(*args, **kwargs)

    return wrapped


@company_bp.route("/dashboard")
@company_required
def dashboard():
    upcoming_drives = PlacementDrive.query.filter(
        PlacementDrive.company_id == current_user.id,
        PlacementDrive.status.in_(["Pending", "Approved"]),
    ).all()
    closed_drives = PlacementDrive.query.filter_by(
        company_id=current_user.id,
        status="Closed",
    ).all()

    return render_template(
        "company/dashboard.html",
        upcoming_drives=upcoming_drives,
        closed_drives=closed_drives,
    )


@company_bp.route("/drive/create", methods=["GET", "POST"])
@company_required
def create_drive():
    if request.method == "POST":
        drive_name = request.form.get("drive_name", "").strip()
        job_title = request.form.get("job_title", "").strip()
        job_description = request.form.get("job_description", "").strip()
        eligibility = request.form.get("eligibility", "").strip()
        salary = request.form.get("salary", "").strip()
        location = request.form.get("location", "").strip()
        deadline_str = request.form.get("application_deadline", "").strip()

        deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()

        drive = PlacementDrive(
            company_id=current_user.id,
            drive_name=drive_name,
            job_title=job_title,
            job_description=job_description,
            eligibility=eligibility,
            salary=salary,
            location=location,
            application_deadline=deadline,
            status="Pending",
        )
        db.session.add(drive)
        db.session.commit()
        flash("Drive created and sent for admin approval.", "success")
        return redirect(url_for("company.dashboard"))

    return render_template("company/create_drive.html")


@company_bp.route("/drive/<int:drive_id>")
@company_required
def drive_details(drive_id: int):
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != current_user.id:
        abort(403)
    return render_template("admin/drive_details.html", drive=drive)


@company_bp.route("/drive/<int:drive_id>/complete", methods=["POST"])
@company_required
def mark_drive_complete(drive_id: int):
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != current_user.id:
        abort(403)

    drive.status = "Closed"
    db.session.commit()
    flash("Drive marked complete.", "info")
    return redirect(url_for("company.dashboard"))


@company_bp.route("/drive/<int:drive_id>/applications")
@company_required
def update_applications(drive_id: int):
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != current_user.id:
        abort(403)

    applications = Application.query.filter_by(drive_id=drive.id).all()
    return render_template(
        "company/update_applications.html",
        drive=drive,
        applications=applications,
    )


@company_bp.route("/application/<int:application_id>", methods=["GET", "POST"])
@company_required
def student_application(application_id: int):
    application = Application.query.get_or_404(application_id)
    if application.drive.company_id != current_user.id:
        abort(403)

    if request.method == "POST":
        action = request.form.get("action")
        if action == "Shortlisted":
            application.status = "Shortlisted"
        elif action == "Rejected":
            application.status = "Rejected"
        else:
            application.status = "Applied"

        db.session.commit()
        flash("Application status updated.", "success")
        return redirect(
            url_for("company.update_applications", drive_id=application.drive_id)
        )

    return render_template("company/student_application.html", application=application)
