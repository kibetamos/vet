from django import forms
from .models import Vaccination

class VaccinationForm(forms.ModelForm):
    class Meta:
        model = Vaccination
        fields = ["livestock", "vaccine_name", "vaccination_date", "next_due_date", "notes"]
        widgets = {
            "vaccination_date": forms.DateInput(attrs={"type": "date"}),
            "next_due_date": forms.DateInput(attrs={"type": "date"}),
        }
