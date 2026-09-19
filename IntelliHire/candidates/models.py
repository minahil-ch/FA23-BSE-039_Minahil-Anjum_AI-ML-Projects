from django.db import models
from django.conf import settings
from django.urls import reverse


def resume_upload_path(instance, filename):
    return f"resumes/{instance.candidate_id or 'temp'}/{filename}"


class Candidate(models.Model):
    """Core candidate profile used for HR management and ML prediction."""

    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        OTHER = "O", "Other"

    class Status(models.TextChoices):
        APPLIED = "APPLIED", "Applied"
        RESUME_SHORTLISTED = "RESUME_SHORTLISTED", "Resume Shortlisted"
        ASSESSMENT_PENDING = "ASSESSMENT_PENDING", "Assessment Pending"
        INTERVIEW_SCHEDULED = "INTERVIEW_SCHEDULED", "Interview Scheduled"
        INTERVIEW_COMPLETED = "INTERVIEW_COMPLETED", "Interview Completed"
        SELECTED = "SELECTED", "Selected"
        REJECTED = "REJECTED", "Rejected"
        HIRED = "HIRED", "Hired"

    candidate_id = models.CharField(max_length=20, unique=True, blank=True)

    # Personal info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=Gender.choices, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    # Education
    highest_qualification = models.CharField(max_length=100)
    university = models.CharField(max_length=200, blank=True)
    graduation_year = models.PositiveIntegerField(blank=True, null=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)

    # Experience
    experience_years = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    current_company = models.CharField(max_length=150, blank=True)
    current_job_title = models.CharField(max_length=150, blank=True)
    expected_salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    current_salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    # Preferences / Skills
    preferred_department = models.CharField(max_length=100, blank=True)
    preferred_job_role = models.CharField(max_length=150, blank=True)
    technical_skills = models.TextField(blank=True, help_text="Comma-separated skills")
    soft_skills = models.TextField(blank=True, help_text="Comma-separated skills")
    programming_languages = models.TextField(blank=True, help_text="Comma-separated languages")
    certifications = models.TextField(blank=True)
    projects = models.TextField(blank=True)

    # Scores (used heavily by the ML model)
    communication_score = models.PositiveSmallIntegerField(default=0, help_text="0-100")
    interview_score = models.PositiveSmallIntegerField(default=0, help_text="0-100")

    # Links
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)

    # Files
    resume_file = models.FileField(upload_to=resume_upload_path, blank=True, null=True)
    profile_photo = models.ImageField(upload_to="candidate_photos/", blank=True, null=True)

    # Process
    application_date = models.DateField(auto_now_add=True)
    interview_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.APPLIED)

    # ML outputs (last prediction cache, optional convenience fields)
    last_prediction = models.CharField(max_length=20, blank=True)
    last_prediction_probability = models.FloatField(blank=True, null=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name="candidates_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.candidate_id:
            last = Candidate.objects.order_by("-id").first()
            next_id = (last.id + 1) if last else 1
            self.candidate_id = f"CAND-{next_id:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.candidate_id} - {self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse("candidates:detail", kwargs={"pk": self.pk})

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def skills_list(self):
        return [s.strip() for s in self.technical_skills.split(",") if s.strip()]
