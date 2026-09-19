from django import forms
from .models import Candidate


class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        exclude = ["candidate_id", "created_by", "application_date",
                   "last_prediction", "last_prediction_probability"]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "interview_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "technical_skills": forms.Textarea(attrs={"rows": 2, "class": "form-control",
                                                        "placeholder": "e.g. Python, SQL, Django"}),
            "soft_skills": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "programming_languages": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "certifications": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "projects": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if "class" not in field.widget.attrs:
                field.widget.attrs["class"] = "form-control"

    def clean_resume_file(self):
        file = self.cleaned_data.get("resume_file")
        if file:
            valid_extensions = [".pdf", ".doc", ".docx"]
            if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError("Only PDF, DOC, or DOCX files are allowed for resumes.")
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Resume file must be smaller than 5MB.")
        return file
