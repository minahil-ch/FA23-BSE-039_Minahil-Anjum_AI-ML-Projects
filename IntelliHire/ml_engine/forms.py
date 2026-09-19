from django import forms
from candidates.models import Candidate


class PredictionForm(forms.Form):
    """Standalone form for HR to manually enter a candidate's info for prediction."""
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    experience_years = forms.DecimalField(min_value=0, max_value=50, initial=0)
    cgpa = forms.DecimalField(min_value=0, max_value=4, initial=3, required=False)
    highest_qualification = forms.ChoiceField(choices=[
        ("bachelor", "Bachelor"), ("master", "Master"), ("phd", "PhD"),
        ("intermediate", "Intermediate"), ("diploma", "Diploma"),
    ])
    communication_score = forms.IntegerField(min_value=0, max_value=100, initial=50)
    interview_score = forms.IntegerField(min_value=0, max_value=100, initial=50)
    technical_skills = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}),
                                        help_text="Comma-separated, e.g. Python, SQL, Django")
    expected_salary = forms.DecimalField(min_value=0, initial=50000, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def to_feature_dict(self):
        data = self.cleaned_data
        return {
            "experience_years": float(data["experience_years"]),
            "cgpa": float(data.get("cgpa") or 0),
            "communication_score": float(data["communication_score"]),
            "interview_score": float(data["interview_score"]),
            "technical_skills": data["technical_skills"],
            "highest_qualification": data["highest_qualification"],
            "expected_salary": float(data.get("expected_salary") or 0),
        }
