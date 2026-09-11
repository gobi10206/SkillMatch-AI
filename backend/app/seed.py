"""
Seeds the database with demo-mode data: a small skill taxonomy,
careers with required skills, courses, demo jobs/internships, and an
admin account. All Job/Course rows are marked is_demo_data=True so
the frontend can label them clearly (Phase 39 rule: never represent
sample data as real employment-market data).

Run with:
    cd backend && python -m app.seed
"""
from app.core.database import SessionLocal, Base, engine
from app.core.security import hash_password
from app.models import (  # noqa: F401 — ensures all tables are registered on Base.metadata
    User, Profile, Skill, Career, CareerSkill, Company, Job, JobSkill, Course, CourseSkill,
)

SKILLS = [
    # (name, category, parent_category, skill_type, synonyms)
    ("Python", "Programming", "Technology", "technical", "python programming"),
    ("Java", "Programming", "Technology", "technical", "java programming"),
    ("JavaScript", "Programming", "Technology", "technical", "js, javascript programming"),
    ("SQL", "Programming", "Technology", "technical", "structured query language, databases"),
    ("Git", "Software Development", "Technology", "technical", "git, github, version control"),
    ("REST APIs", "Software Development", "Technology", "technical", "rest api, restful api, api development"),
    ("Testing", "Software Development", "Technology", "technical", "unit testing, qa, quality assurance"),
    ("Spring Boot", "Software Development", "Technology", "technical", "spring boot, spring framework"),
    ("Docker", "Cloud", "Technology", "technical", "containers, containerization"),
    ("AWS", "Cloud", "Technology", "technical", "amazon web services"),
    ("Computer Troubleshooting", "IT Support", "Technology", "technical", "debugging computers, fixing computers, repairing computers, troubleshoot"),
    ("Technical Support", "IT Support", "Technology", "technical", "tech support, help desk, it support"),
    ("Customer Service", "Soft Skills", None, "soft", "customer support, customer management, client service"),
    ("Computer Literacy", "IT Support", "Technology", "technical", "basic computer usage, computer skills"),
    ("Inventory Management", "Business Operations", None, "technical", "inventory, stock management"),
    ("Basic Accounting", "Business Operations", None, "technical", "billing, bookkeeping, accounts"),
    ("Teaching", "Soft Skills", None, "soft", "training, tutoring, instructing"),
    ("Problem Solving", "Soft Skills", None, "soft", "troubleshooting, critical thinking"),
    ("Communication", "Soft Skills", None, "soft", "verbal communication, written communication"),
    ("Data Visualization", "Data", "Technology", "technical", "charts, dashboards, power bi"),
    ("Pandas", "Data", "Technology", "technical", "pandas library, dataframes"),
    ("Statistics", "Data", "Technology", "technical", "statistical analysis"),
    ("Excel", "Data", "Technology", "technical", "microsoft excel, spreadsheets"),
]

CAREERS = [
    ("IT Support Technician", "Technology", [
        ("Computer Troubleshooting", True), ("Technical Support", True),
        ("Customer Service", True), ("Computer Literacy", True), ("Problem Solving", False),
    ]),
    ("Software Developer", "Technology", [
        ("Java", True), ("Git", True), ("REST APIs", True), ("SQL", True),
        ("Spring Boot", True), ("Testing", False),
    ]),
    ("Backend Developer", "Technology", [
        ("Java", True), ("SQL", True), ("REST APIs", True), ("Spring Boot", True),
        ("Git", True), ("Testing", True), ("Docker", False),
    ]),
    ("Data Analyst", "Technology", [
        ("Excel", True), ("SQL", True), ("Statistics", True),
        ("Pandas", True), ("Data Visualization", True), ("Python", False),
    ]),
]

COURSES = [
    ("Spring Boot Fundamentals", "Demo Catalog", ["Spring Boot"]),
    ("SQL for Beginners", "Demo Catalog", ["SQL"]),
    ("REST API Design", "Demo Catalog", ["REST APIs"]),
    ("Intro to Data Visualization", "Demo Catalog", ["Data Visualization"]),
    ("Python for Data Analysis", "Demo Catalog", ["Python", "Pandas"]),
    ("IT Help Desk Essentials", "Demo Catalog", ["Technical Support", "Computer Troubleshooting"]),
]

DEMO_JOBS = [
    ("Java Developer", "Software Developer", "Demo Tech Co", "full_time", "Remote", True, "entry",
     ["Java", "Spring Boot", "SQL", "Git", "REST APIs"]),
    ("IT Support Associate", "IT Support Technician", "Demo Retail Inc", "full_time", "Chennai, India", False, "entry",
     ["Computer Troubleshooting", "Technical Support", "Customer Service"]),
    ("Data Analyst Intern", "Data Analyst", "Demo Analytics Ltd", "internship", "Bengaluru, India", True, "internship",
     ["Excel", "SQL", "Statistics"]),
]


def seed():
    Base.metadata.create_all(bind=engine)  # safety net if migrations weren't run
    db = SessionLocal()
    try:
        if db.query(Skill).first():
            print("Demo data already present — skipping seed.")
            return

        skill_objs = {}
        for name, category, parent, skill_type, synonyms in SKILLS:
            s = Skill(name=name, category=category, parent_category=parent, skill_type=skill_type, synonyms=synonyms)
            db.add(s)
            skill_objs[name] = s
        db.flush()

        career_objs = {}
        for title, industry, req_skills in CAREERS:
            c = Career(title=title, industry=industry, description=f"Demo career profile for {title}.")
            db.add(c)
            db.flush()
            for skill_name, is_required in req_skills:
                db.add(CareerSkill(career_id=c.id, skill_id=skill_objs[skill_name].id, is_required=is_required))
            career_objs[title] = c

        for title, provider, skill_names in COURSES:
            course = Course(title=title, provider=f"External: {provider}", is_external=True, is_demo_data=True,
                             description=f"Demo course covering {', '.join(skill_names)}.")
            db.add(course)
            db.flush()
            for skill_name in skill_names:
                db.add(CourseSkill(course_id=course.id, skill_id=skill_objs[skill_name].id))

        admin_user = User(
            email="admin@skillmatch.demo", hashed_password=hash_password("ChangeMe123!"),
            full_name="Demo Admin", role="admin", is_active=True, is_verified=True,
        )
        db.add(admin_user)

        employer_user = User(
            email="employer@skillmatch.demo", hashed_password=hash_password("ChangeMe123!"),
            full_name="Demo Employer", role="employer", is_active=True, is_verified=True,
        )
        db.add(employer_user)
        db.flush()

        company = Company(owner_user_id=employer_user.id, name="Demo Tech Co", description="Seeded demo company.")
        db.add(company)
        db.flush()

        for title, career_title, company_name, job_type, location, is_remote, exp_level, skill_names in DEMO_JOBS:
            job = Job(
                company_id=company.id, title=title, job_type=job_type, location=location,
                is_remote=is_remote, experience_level=exp_level, is_demo_data=True,
                description=f"Demo {job_type.replace('_', ' ')} posting aligned with the {career_title} career path.",
            )
            db.add(job)
            db.flush()
            for skill_name in skill_names:
                db.add(JobSkill(job_id=job.id, skill_id=skill_objs[skill_name].id, is_required=True))

        db.commit()
        print("Demo data seeded: skills, careers, courses, demo jobs, admin + employer accounts.")
        print("Admin login: admin@skillmatch.demo / ChangeMe123!  (demo only — change or remove in production)")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
