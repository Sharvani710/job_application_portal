from datetime import date, timedelta

from app import create_app
from extensions import db
from models import Application, Company, PlacementDrive, Student


def get_or_create_company(
    company_name: str,
    hr_contact: str,
    website: str,
    email: str,
    password: str,
    approval_status: str,
    is_blacklisted: bool = False,
):
    company = Company.query.filter_by(email=email).first()
    if company:
        return company

    company = Company(
        company_name=company_name,
        hr_contact=hr_contact,
        website=website,
        email=email,
        approval_status=approval_status,
        is_blacklisted=is_blacklisted,
    )
    company.set_password(password)
    db.session.add(company)
    db.session.flush()
    return company


def get_or_create_student(
    name: str,
    email: str,
    department: str,
    password: str,
    resume: str,
    is_blacklisted: bool = False,
):
    student = Student.query.filter_by(email=email).first()
    if student:
        return student

    student = Student(
        name=name,
        email=email,
        department=department,
        resume=resume,
        is_blacklisted=is_blacklisted,
    )
    student.set_password(password)
    db.session.add(student)
    db.session.flush()
    return student


def get_or_create_drive(
    company_id: int,
    drive_name: str,
    job_title: str,
    job_description: str,
    eligibility: str,
    salary: str,
    location: str,
    application_deadline: date,
    status: str,
):
    drive = PlacementDrive.query.filter_by(
        company_id=company_id,
        drive_name=drive_name,
    ).first()
    if drive:
        return drive

    drive = PlacementDrive(
        company_id=company_id,
        drive_name=drive_name,
        job_title=job_title,
        job_description=job_description,
        eligibility=eligibility,
        salary=salary,
        location=location,
        application_deadline=application_deadline,
        status=status,
    )
    db.session.add(drive)
    db.session.flush()
    return drive


def get_or_create_application(student_id: int, drive_id: int, status: str):
    app = Application.query.filter_by(student_id=student_id, drive_id=drive_id).first()
    if app:
        return app

    app = Application(
        student_id=student_id,
        drive_id=drive_id,
        application_date=date.today() - timedelta(days=2),
        status=status,
    )
    db.session.add(app)
    return app


def seed_dummy_data() -> None:
    acme = get_or_create_company(
        company_name="Acme Technologies",
        hr_contact="Riya Sharma",
        website="https://acme.example.com",
        email="acme@company.com",
        password="company123",
        approval_status="Approved",
    )
    byteworks = get_or_create_company(
        company_name="ByteWorks Pvt Ltd",
        hr_contact="Amit Rao",
        website="https://byteworks.example.com",
        email="byteworks@company.com",
        password="company123",
        approval_status="Approved",
    )
    pending_co = get_or_create_company(
        company_name="FutureSoft Labs",
        hr_contact="Neha Kapoor",
        website="https://futuresoft.example.com",
        email="futuresoft@company.com",
        password="company123",
        approval_status="Pending",
    )
    get_or_create_company(
        company_name="Nova Systems",
        hr_contact="Isha Reddy",
        website="https://novasystems.example.com",
        email="nova@company.com",
        password="company123",
        approval_status="Approved",
    )
    get_or_create_company(
        company_name="Skyline Dynamics",
        hr_contact="Rahul Menon",
        website="https://skyline.example.com",
        email="skyline@company.com",
        password="company123",
        approval_status="Approved",
    )
    get_or_create_company(
        company_name="OrbitWorks",
        hr_contact="Sneha Rao",
        website="https://orbitworks.example.com",
        email="orbitworks@company.com",
        password="company123",
        approval_status="Pending",
    )
    get_or_create_company(
        company_name="Zenith Tech",
        hr_contact="Aditya Singh",
        website="https://zenithtech.example.com",
        email="zenith@company.com",
        password="company123",
        approval_status="Approved",
    )

    s1 = get_or_create_student(
        name="Aarav Mehta",
        email="aarav@student.com",
        department="Computer Science",
        password="student123",
        resume="https://example.com/resume/aarav",
    )
    s2 = get_or_create_student(
        name="Priya Nair",
        email="priya@student.com",
        department="Information Technology",
        password="student123",
        resume="https://example.com/resume/priya",
    )
    s3 = get_or_create_student(
        name="Kunal Verma",
        email="kunal@student.com",
        department="Electronics",
        password="student123",
        resume="https://example.com/resume/kunal",
    )

    d1 = get_or_create_drive(
        company_id=acme.id,
        drive_name="Acme Campus Drive 2026",
        job_title="Software Development Engineer",
        job_description="Backend role focused on Flask and APIs.",
        eligibility="CSE/IT, CGPA 7.0+",
        salary="8 LPA",
        location="Bengaluru",
        application_deadline=date.today() + timedelta(days=12),
        status="Approved",
    )
    d2 = get_or_create_drive(
        company_id=acme.id,
        drive_name="Acme Data Analyst Drive",
        job_title="Data Analyst",
        job_description="Analytics and dashboard reporting role.",
        eligibility="Any branch, CGPA 6.5+",
        salary="6 LPA",
        location="Hyderabad",
        application_deadline=date.today() + timedelta(days=8),
        status="Closed",
    )
    d3 = get_or_create_drive(
        company_id=byteworks.id,
        drive_name="ByteWorks Graduate Engineer Program",
        job_title="Graduate Engineer Trainee",
        job_description="Rotational engineering program.",
        eligibility="CSE/IT/ECE, CGPA 6.0+",
        salary="5.5 LPA",
        location="Pune",
        application_deadline=date.today() + timedelta(days=15),
        status="Approved",
    )
    get_or_create_drive(
        company_id=pending_co.id,
        drive_name="FutureSoft Product Internship",
        job_title="Product Intern",
        job_description="Internship with PPO opportunity.",
        eligibility="All branches",
        salary="Stipend 25k/month",
        location="Remote",
        application_deadline=date.today() + timedelta(days=20),
        status="Pending",
    )

    get_or_create_application(student_id=s1.id, drive_id=d1.id, status="Applied")
    get_or_create_application(student_id=s2.id, drive_id=d1.id, status="Shortlisted")
    get_or_create_application(student_id=s3.id, drive_id=d3.id, status="Rejected")
    get_or_create_application(student_id=s1.id, drive_id=d2.id, status="Selected")

    db.session.commit()


def main() -> None:
    app = create_app()
    with app.app_context():
        seed_dummy_data()
        print("Dummy data seeded successfully.")
        print("Admin login: admin / admin123")
        print("Company logins: acme@company.com / company123, byteworks@company.com / company123")
        print("Student logins: aarav@student.com / student123, priya@student.com / student123")


if __name__ == "__main__":
    main()
