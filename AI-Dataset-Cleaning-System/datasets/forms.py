"""Forms for dataset upload and cleaning."""

from django import forms

from .models import Dataset


class DatasetUploadForm(forms.ModelForm):
    """Upload CSV or Excel dataset."""

    class Meta:
        model = Dataset
        fields = ('name', 'original_file')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dataset name',
            }),
            'original_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.csv,.xlsx,.xls',
            }),
        }


class CleaningOperationsForm(forms.Form):
    """Select cleaning operations to apply."""

    OPERATION_CHOICES = [
        ('remove_duplicates', 'Remove Duplicates'),
        ('fill_missing_mean', 'Fill Missing (Mean)'),
        ('fill_missing_median', 'Fill Missing (Median)'),
        ('fill_missing_mode', 'Fill Missing (Mode)'),
        ('remove_missing', 'Remove Missing Values'),
        ('normalize_text', 'Normalize Text'),
        ('remove_extra_spaces', 'Remove Extra Spaces'),
        ('encode_categorical', 'Encode Categorical'),
        ('scale_numeric', 'Scale Numeric Values'),
        ('remove_outliers', 'Remove Outliers'),
    ]

    operations = forms.MultipleChoiceField(
        choices=OPERATION_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    use_ai_suggestions = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Apply AI-suggested cleaning operations',
    )

    def get_operations_list(self):
        """Convert form selections to operation dicts."""
        selected = self.cleaned_data.get('operations', [])
        ops = []

        op_map = {
            'remove_duplicates': {'name': 'remove_duplicates', 'params': {}},
            'fill_missing_mean': {'name': 'fill_missing', 'params': {'method': 'mean'}},
            'fill_missing_median': {'name': 'fill_missing', 'params': {'method': 'median'}},
            'fill_missing_mode': {'name': 'fill_missing', 'params': {'method': 'mode'}},
            'remove_missing': {'name': 'remove_missing', 'params': {}},
            'normalize_text': {'name': 'normalize_text', 'params': {'case': 'lower'}},
            'remove_extra_spaces': {'name': 'remove_extra_spaces', 'params': {}},
            'encode_categorical': {'name': 'encode_categorical', 'params': {}},
            'scale_numeric': {'name': 'scale_numeric', 'params': {'method': 'standard'}},
            'remove_outliers': {'name': 'remove_outliers', 'params': {'method': 'isolation_forest'}},
        }

        for key in selected:
            if key in op_map:
                ops.append(op_map[key])

        return ops
