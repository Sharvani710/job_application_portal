from datetime import date

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class Admin(UserMixin, db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, raw_password: str) -> None:
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password, raw_password)

    @property
    def role(self) -> str:
        return "admin"

    def get_id(self) -> str:
        return f"admin-{self.id}"


class Student(UserMixin, db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    resume = db.Column(db.Text, nullable=True)
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)

    applications = db.relationship("Application", back_populates="student", cascade="all, delete-orphan")

    def set_password(self, raw_password: str) -> None:
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password, raw_password)

    @property
    def role(self) -> str:
        return "student"

    def get_id(self) -> str:
        return f"student-{self.id}"


class Company(UserMixin, db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150), nullable=False)
    hr_contact = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    approval_status = db.Column(db.String(30), default="Pending", nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)

    drives = db.relationship("PlacementDrive", back_populates="company", cascade="all, delete-orphan")

    def set_password(self, raw_password: str) -> None:
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password, raw_password)

    @property
    def role(self) -> str:
        return "company"

    def get_id(self) -> str:
        return f"company-{self.id}"


class PlacementDrive(db.Model):
    __tablename__ = "placement_drives"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    drive_name = db.Column(db.String(150), nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    eligibility = db.Column(db.Text, nullable=False)
    salary = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    application_deadline = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(30), default="Pending", nullable=False)

    company = db.relationship("Company", back_populates="drives")
    applications = db.relationship("Application", back_populates="drive", cascade="all, delete-orphan")


class Application(db.Model):
    __tablename__ = "applications"
    __table_args__ = (
        db.UniqueConstraint("student_id", "drive_id", name="uq_student_drive"),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drives.id"), nullable=False)
    application_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(30), nullable=False, default="Applied")

    student = db.relationship("Student", back_populates="applications")
    drive = db.relationship("PlacementDrive", back_populates="applications")
