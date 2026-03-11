from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from extensions import db
from models import Application, Company, PlacementDrive, Student


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user.role != "admin":
            abort(403)
        return view_func(*args, **kwargs)

    return wrapped


@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    companies = Company.query.order_by(Company.company_name.asc()).all()
    students = Student.query.order_by(Student.name.asc()).all()
    pending_companies = Company.query.filter_by(approval_status="Pending").all()
    pending_drives = PlacementDrive.query.filter_by(status="Pending").all()
    ongoing_drives = PlacementDrive.query.filter(
        PlacementDrive.status.in_(["Approved"])
    ).all()
    applications = Application.query.order_by(Application.application_date.desc()).all()

    return render_template(
        "admin/dashboard.html",
        companies=companies,
        students=students,
        pending_companies=pending_companies,
        pending_drives=pending_drives,
        ongoing_drives=ongoing_drives,
        applications=applications,
    )


@admin_bp.route("/company/<int:company_id>")
@admin_required
def company_details(company_id: int):
    company = Company.query.get_or_404(company_id)
    return render_template("admin/company_details.html", company=company)


@admin_bp.route("/student/<int:student_id>")
@admin_required
def student_details(student_id: int):
    student = Student.query.get_or_404(student_id)
    return render_template("admin/student_details.html", student=student)


@admin_bp.route("/drive/<int:drive_id>")
@admin_required
def drive_details(drive_id: int):
    drive = PlacementDrive.query.get_or_404(drive_id)
    return render_template("admin/drive_details.html", drive=drive)


@admin_bp.route("/company/<int:company_id>/approve", methods=["POST"])
@admin_required
def approve_company(company_id: int):
    company = Company.query.get_or_404(company_id)
    company.approval_status = "Approved"
    db.session.commit()
    flash("Company approved.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/company/<int:company_id>/blacklist", methods=["POST"])
@admin_required
def blacklist_company(company_id: int):
    company = Company.query.get_or_404(company_id)
    company.is_blacklisted = not company.is_blacklisted
    db.session.commit()
    flash("Company blacklist status updated.", "warning")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/student/<int:student_id>/blacklist", methods=["POST"])
@admin_required
def blacklist_student(student_id: int):
    student = Student.query.get_or_404(student_id)
    student.is_blacklisted = not student.is_blacklisted
    db.session.commit()
    flash("Student blacklist status updated.", "warning")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/drive/<int:drive_id>/approve", methods=["POST"])
@admin_required
def approve_drive(drive_id: int):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "Approved"
    db.session.commit()
    flash("Drive approved.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/drive/<int:drive_id>/complete", methods=["POST"])
@admin_required
def complete_drive(drive_id: int):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "Closed"
    db.session.commit()
    flash("Drive marked as closed.", "info")
    return redirect(url_for("admin.dashboard"))
