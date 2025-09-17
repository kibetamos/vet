from django import forms
from .models import *
from django.contrib.auth import get_user_model

User = get_user_model()

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["farmer", "vet", "livestock", "date", "purpose", "status"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "farmer": forms.Select(attrs={"class": "form-control"}),
            "vet": forms.Select(attrs={"class": "form-control"}),
            "livestock": forms.Select(attrs={"class": "form-control"}),
            "purpose": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # If the user is a farmer, limit livestock choices to their own
        if user and getattr(user, "role", "") == "farmer":
            self.fields["livestock"].queryset = Livestock.objects.filter(farmer=user)
        else:
            self.fields["livestock"].queryset = Livestock.objects.all()

            
class VaccinationForm(forms.ModelForm):
    class Meta:
        model = Vaccination
        fields = ["livestock", "vaccine_name", "vaccination_date", "next_due_date", "notes"]
        widgets = {
            "livestock": forms.Select(attrs={"class": "form-control"}),
            "vaccine_name": forms.TextInput(attrs={"class": "form-control"}),
            "vaccination_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "next_due_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)  # ✅ extract 'user'
        super().__init__(*args, **kwargs)

        # Restrict livestock selection if the user is a farmer
        if user and getattr(user, "role", "") == "farmer":
            self.fields["livestock"].queryset = Livestock.objects.filter(farmer=user)

class LivestockForm(forms.ModelForm):
    class Meta:
        model = Livestock
        fields = ["name", "livestock_type", "breed", "date_of_birth", "weight", "notes"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "livestock_type": forms.Select(attrs={"class": "form-control"}),
            "breed": forms.TextInput(attrs={"class": "form-control"}),
            "date_of_birth": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "weight": forms.NumberInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }


# class TreatmentForm(forms.ModelForm):
#     class Meta:
#         model = Treatment
#         fields = ["livestock", "treatment_date", "description", "medication", "cost"]
#         widgets = {
#             "treatment_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
#             "livestock": forms.Select(attrs={"class": "form-control"}),
#             "description": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
#             "medication": forms.TextInput(attrs={"class": "form-control"}),
#             "cost": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
#         }

class TreatmentForm(forms.ModelForm):
    # extra field only for MPESA
    phone_number = forms.CharField(
        max_length=12,
        label="Farmer Phone Number",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. 2547XXXXXXXX"
        })
    )

    class Meta:
        model = Treatment
        fields = ["livestock", "treatment_date", "description", "medication", "cost", "phone_number"]
        widgets = {
            "treatment_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "livestock": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "medication": forms.TextInput(attrs={"class": "form-control"}),
            "cost": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }
