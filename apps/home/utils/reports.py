from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from openpyxl import Workbook
from apps.home.models import Livestock, Vaccination, Treatment, Appointment


def generate_farmer_report_pdf(user):
    """Generate a PDF report for a farmer."""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, height - 50, "Farmer Report")

    # Farmer info
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 100, f"Farmer Name: {user.get_full_name() or user.username}")
    p.drawString(50, height - 120, f"Email: {user.email}")

    # Livestock info
    livestock = Livestock.objects.filter(farmer=user)
    p.drawString(50, height - 150, f"Total Livestock: {livestock.count()}")
    p.drawString(50, height - 170, "Livestock Breakdown:")
    y = height - 190
    for animal_type in livestock.values_list("livestock_type", flat=True).distinct():
        count = livestock.filter(livestock_type=animal_type).count()
        p.drawString(70, y, f"{animal_type.capitalize()}: {count}")
        y -= 20

    # Recent vaccinations
    vaccinations = Vaccination.objects.filter(livestock__farmer=user).order_by("-vaccination_date")[:5]
    p.drawString(50, y - 20, "Recent Vaccinations:")
    y -= 40
    for v in vaccinations:
        p.drawString(70, y, f"{v.livestock.name} - {v.vaccine_name} ({v.vaccination_date})")
        y -= 20

    # Recent treatments — FIXED: Removed treatment_type
    treatments = Treatment.objects.filter(livestock__farmer=user).order_by("-treatment_date")[:5]
    p.drawString(50, y - 20, "Recent Treatments:")
    y -= 40
    for t in treatments:
        medication = t.medication if t.medication else "No medication"
        p.drawString(70, y, f"{t.livestock.name} - {medication} ({t.treatment_date})")
        y -= 20

    # Finalize PDF
    p.showPage()
    p.save()

    buffer.seek(0)
    return HttpResponse(buffer, content_type="application/pdf")


def generate_vet_report_excel(user):
    """Generate an Excel report for a vet."""
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Vet Report"

    # Headers
    headers = ["Vet Name", "Email", "Total Livestock", "Vaccinations", "Treatments", "Appointments"]
    sheet.append(headers)

    # Stats
    total_livestock = Livestock.objects.count()
    vaccinations = Vaccination.objects.filter(vet=user).count()
    treatments = Treatment.objects.filter(vet=user).count()
    appointments = Appointment.objects.filter(vet=user).count()

    # Data row
    sheet.append([
        user.get_full_name() or user.username,
        user.email,
        total_livestock,
        vaccinations,
        treatments,
        appointments,
    ])

    # Send file
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="vet_report_{user.username}.xlsx"'
    workbook.save(response)
    return response
