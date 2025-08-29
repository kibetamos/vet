from django.db import models
from django.contrib.auth.models import AbstractUser

# ---------------------------------------------------------
# Custom User Model
# ---------------------------------------------------------
def user_picture_path(instance, filename):
    return f'user_pictures/user_{instance.id}/{filename}'

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('farmer', 'Farmer'),
        ('vet', 'Vet Doctor'),
        ('staff', 'Staff'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='farmer')
    user_picture = models.ImageField(upload_to=user_picture_path, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True) 
    
    def __str__(self):
        return self.username


# ---------------------------------------------------------
# Farmer & Livestock Records
# ---------------------------------------------------------
class Livestock(models.Model):
    LIVESTOCK_TYPES = [
        ('cattle', 'Cattle'),
        ('goat', 'Goat'),
        ('sheep', 'Sheep'),
        ('poultry', 'Poultry'),
        ('other', 'Other'),
    ]

    farmer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'farmer'})
    name = models.CharField(max_length=100)
    livestock_type = models.CharField(max_length=20, choices=LIVESTOCK_TYPES)
    breed = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.livestock_type})"


# ---------------------------------------------------------
# Appointments between Vet and Farmer
# ---------------------------------------------------------
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="farmer_appointments",
                               limit_choices_to={'role': 'farmer'})
    vet = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vet_appointments",
                            limit_choices_to={'role': 'vet'})
    livestock = models.ForeignKey(Livestock, on_delete=models.CASCADE)
    date = models.DateTimeField()
    purpose = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Appointment with {self.vet.username} on {self.date}"


# ---------------------------------------------------------
# Treatment Records
# ---------------------------------------------------------
class Treatment(models.Model):
    livestock = models.ForeignKey(Livestock, on_delete=models.CASCADE)
    vet = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'vet'})
    treatment_date = models.DateField()
    description = models.TextField()
    medication = models.CharField(max_length=200, blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Treatment for {self.livestock.name} on {self.treatment_date}"


# ---------------------------------------------------------
# Vaccination Records
# ---------------------------------------------------------
class Vaccination(models.Model):
    livestock = models.ForeignKey(Livestock, on_delete=models.CASCADE)
    vet = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'vet'})
    vaccine_name = models.CharField(max_length=200)
    vaccination_date = models.DateField()
    next_due_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.vaccine_name} for {self.livestock.name}"


# ---------------------------------------------------------
# Reports
# ---------------------------------------------------------
class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('treatment', 'Treatment'),
        ('vaccination', 'Vaccination'),
        ('general', 'General'),
    ]
    livestock = models.ForeignKey(Livestock, on_delete=models.CASCADE)
    vet = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'vet'})
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.report_type} report for {self.livestock.name}"
