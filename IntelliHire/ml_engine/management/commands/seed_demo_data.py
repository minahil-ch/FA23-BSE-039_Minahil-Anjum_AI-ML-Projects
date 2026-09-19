"""
Management command to seed the database with demo data so the project
can be explored/graded immediately: an admin user, sample candidates,
and a ready-to-train sample recruitment dataset CSV.

Usage: python manage.py seed_demo_data
"""
import os
import random
import csv
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from candidates.models import Candidate

User = get_user_model()

FIRST_NAMES = ["Ali", "Sara", "Ahmed", "Ayesha", "Bilal", "Hina", "Usman", "Zara",
               "Hamza", "Mahnoor", "Omar", "Fatima", "Danish", "Sana", "Farhan", "Iqra"]
LAST_NAMES = ["Khan", "Malik", "Raza", "Butt", "Sheikh", "Iqbal", "Chaudhry", "Farooq"]
DEPARTMENTS = ["Software Engineering", "Data Science", "Marketing", "Human Resources", "Finance", "Sales"]
QUALIFICATIONS = ["bachelor", "master", "phd", "intermediate", "diploma"]
SKILLS_POOL = ["Python", "Django", "SQL", "JavaScript", "React", "Machine Learning",
               "Excel", "Communication", "Java", "AWS", "Docker", "Data Analysis"]


class Command(BaseCommand):
    help = "Seed demo users, candidates, and a sample ML training dataset."

    def add_arguments(self, parser):
        parser.add_argument("--candidates", type=int, default=60)

    def handle(self, *args, **options):
        self.create_admin()
        self.create_candidates(options["candidates"])
        self.create_sample_dataset_csv(options["candidates"])
        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))

    def create_admin(self):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin", email="admin@intellihire.com", password="Admin@12345",
                role=User.Role.ADMIN, first_name="System", last_name="Admin"
            )
            self.stdout.write("Created admin user -> username: admin / password: Admin@12345")
        if not User.objects.filter(username="hr_manager").exists():
            User.objects.create_user(
                username="hr_manager", email="hr@intellihire.com", password="Hr@12345",
                role=User.Role.HR_MANAGER, first_name="HR", last_name="Manager"
            )
            self.stdout.write("Created HR user -> username: hr_manager / password: Hr@12345")

    def _random_candidate_row(self, i):
        fn, ln = random.choice(FIRST_NAMES), random.choice(LAST_NAMES)
        exp = round(random.uniform(0, 12), 1)
        cgpa = round(random.uniform(2.2, 4.0), 2)
        comm = random.randint(30, 100)
        interview = random.randint(20, 100)
        n_skills = random.randint(1, 6)
        skills = ", ".join(random.sample(SKILLS_POOL, n_skills))
        qualification = random.choice(QUALIFICATIONS)
        salary = random.randint(30000, 200000)

        # A simple, semi-realistic rule to generate a plausible ground-truth
        # label for demo purposes (real projects should use real HR outcome data).
        # Score range is roughly 54-165 given the input ranges above, so we use
        # the midpoint (~110) as the cutoff, plus a little randomness so the
        # boundary isn't perfectly sharp (more realistic for ML training).
        score = (exp * 4) + (cgpa * 10) + (comm * 0.3) + (interview * 0.4) + (n_skills * 3)
        score += random.uniform(-15, 15)
        selected = 1 if score > 110 else 0

        return {
            "first_name": fn, "last_name": ln,
            "email": f"{fn.lower()}.{ln.lower()}{i}@example.com",
            "phone_number": f"03{random.randint(100000000, 999999999)}",
            "gender": random.choice(["M", "F"]),
            "highest_qualification": qualification,
            "university": "Sample University",
            "graduation_year": random.randint(2016, 2025),
            "cgpa": cgpa,
            "experience_years": exp,
            "preferred_department": random.choice(DEPARTMENTS),
            "technical_skills": skills,
            "technical_skills_count": n_skills,
            "communication_score": comm,
            "interview_score": interview,
            "expected_salary": salary,
            "qualification_level": {"matric": 1, "intermediate": 2, "diploma": 2,
                                     "bachelor": 3, "master": 4, "phd": 5}[qualification],
            "selected": selected,
        }

    def create_candidates(self, n):
        if Candidate.objects.exists():
            self.stdout.write("Candidates already exist, skipping candidate seeding.")
            return
        for i in range(n):
            row = self._random_candidate_row(i)
            Candidate.objects.create(
                first_name=row["first_name"], last_name=row["last_name"], email=row["email"],
                phone_number=row["phone_number"], gender=row["gender"],
                highest_qualification=row["highest_qualification"], university=row["university"],
                graduation_year=row["graduation_year"], cgpa=row["cgpa"],
                experience_years=row["experience_years"],
                preferred_department=row["preferred_department"],
                technical_skills=row["technical_skills"],
                communication_score=row["communication_score"],
                interview_score=row["interview_score"],
                expected_salary=row["expected_salary"],
                status=Candidate.Status.SELECTED if row["selected"] else Candidate.Status.REJECTED,
            )
        self.stdout.write(f"Created {n} sample candidates.")

    def create_sample_dataset_csv(self, n):
        sample_dir = os.path.join(settings.BASE_DIR, "sample_data")
        os.makedirs(sample_dir, exist_ok=True)
        csv_path = os.path.join(sample_dir, "sample_recruitment_dataset.csv")

        fieldnames = ["first_name", "last_name", "email", "phone_number", "gender",
                      "highest_qualification", "university", "graduation_year", "cgpa",
                      "experience_years", "preferred_department", "technical_skills",
                      "technical_skills_count", "communication_score", "interview_score",
                      "expected_salary", "qualification_level", "selected"]

        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for i in range(300):
                writer.writerow(self._random_candidate_row(i + 1000))

        self.stdout.write(f"Sample training dataset written to: {csv_path}")
        self.stdout.write("Upload this file on the Datasets page to try model training.")
