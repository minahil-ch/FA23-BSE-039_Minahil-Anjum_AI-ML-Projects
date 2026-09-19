from django import forms
from .models import Dataset


class DatasetUploadForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ["name", "file"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Recruitment Dataset 2026"}),
        }

    def clean_file(self):
        file = self.cleaned_data["file"]
        if not file.name.lower().endswith(".csv"):
            raise forms.ValidationError("Only CSV files are supported.")
        if file.size > 20 * 1024 * 1024:
            raise forms.ValidationError("Dataset file must be smaller than 20MB.")
        return file
