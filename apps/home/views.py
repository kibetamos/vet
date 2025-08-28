# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import messages
from django.utils import timezone
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect

from django.urls import reverse_lazy
from apps.home.forms import VaccinationForm
from apps.home.models import *


@login_required(login_url="/login/")
# def index(request):
#     context = {'segment': 'index'}

#     html_template = loader.get_template('home/index.html')
#     return HttpResponse(html_template.render(context, request))


# @login_required(login_url="/login/")
def index(request):
    user_role = getattr(request.user, "role", None)

    if user_role == 'admin':
        return redirect('admin_dashboard')
    
    elif user_role == 'staff':
        return redirect('staff_dashboard')
    
    elif user_role == 'farmer':
        return redirect('farmer_dashboard')
    

    elif user_role == 'vet':
        return redirect('vet_dashboard')
    

    else:
        return render(request, "home/page-403.html") 

@login_required(login_url="/login/")

def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))



# Admin Dashboard View
@login_required(login_url="/login/")
def admin_dashboard(request):
    # return render(request, "admin/admin_dashboard.html")
    return render(request, "home/index.html")

# Staff Dashboard View
@login_required(login_url="/login/")
def staff_dashboard(request):
    # livestock = Livestock.objects.all()
    # return render(request, "staff/staff_dashboard.html",{'livestock': livestock})
    user = request.user

    if user.is_staff:  # Admin can see all livestock
        total_livestock = Livestock.objects.count()
    elif hasattr(user, 'is_vet') and user.is_vet:  # Vet sees livestock assigned to them
        total_livestock = Livestock.objects.filter(assigned_vet=user).count()
    else:  # Farmer sees only their livestock
        total_livestock = Livestock.objects.filter(owner=user).count()

    return render(request,  "staff/staff_dashboard.html", {'total_livestock': total_livestock})


# Farmer Dashboard View
# @login_required(login_url="/login/")
# def farmer_dashboard(request):
#     user = request.user

#     if user.is_staff:  # Admin can see all livestock
#         total_livestock = Livestock.objects.count()
#     elif hasattr(user, 'is_vet') and user.is_vet:  # Vet sees livestock assigned to them
#         total_livestock = Livestock.objects.filter(assigned_vet=user).count()
#     else:  # Farmer sees only their livestock
#         total_livestock = Livestock.objects.filter(owner=user).count()

#     return render(request,  "farmer/farmer_dashboard.html", {'total_livestock': total_livestock})

@login_required(login_url="/login/")
def farmer_dashboard(request):
    user = request.user

    # Base queryset depending on the user role
    if user.is_staff:  # Admin sees all livestock
        livestock_qs = Livestock.objects.all()
    elif user.role == 'vet':  # Vet sees livestock assigned to them (if implemented)
        # If you have no assigned_vet field, vets see all livestock for now
        livestock_qs = Livestock.objects.all()
    else:  # Farmer sees only their livestock
        livestock_qs = Livestock.objects.filter(farmer=user)

    # Counts by livestock type (use the actual DB field: livestock_type)
    total_livestock = livestock_qs.count()
    total_cattle = livestock_qs.filter(livestock_type="cattle").count()
    total_sheep = livestock_qs.filter(livestock_type="sheep").count()
    total_goats = livestock_qs.filter(livestock_type="goat").count()
    total_poultry = livestock_qs.filter(livestock_type="poultry").count()
    total_other = livestock_qs.filter(livestock_type="other").count()

    context = {
        "total_livestock": total_livestock,
        "total_cattle": total_cattle,
        "total_sheep": total_sheep,
        "total_goats": total_goats,
        "total_poultry": total_poultry,
        "total_other": total_other,
    }

    return render(request, "farmer/farmer_dashboard.html", context)

@login_required
def livestock_list(request):
    if request.user.is_authenticated:
        # Show only the livestock belonging to the logged-in farmer
        livestock = Livestock.objects.filter(farmer=request.user)
    else:
        livestock = Livestock.objects.none()
    
    return render(request, 'farmer/livestock.html', {'livestock': livestock})

def vaccination_list(request):
    user = request.user

    # Admins see all vaccinations
    if user.is_superuser:
        vaccinations = Vaccination.objects.all()

    # Farmers see only vaccinations of their livestock
    elif hasattr(user, 'farmer'):
        vaccinations = Vaccination.objects.filter(livestock__farmer=user.farmer)

    # Vets see only vaccinations of livestock they're assigned to
    elif hasattr(user, 'vet'):
        vaccinations = Vaccination.objects.filter(livestock__appointment__vet=user.vet).distinct()

    else:
        vaccinations = Vaccination.objects.none()

    return render(request, "farmer/vaccination_list.html", {"vaccinations": vaccinations})


@login_required(login_url="/login/")
def vet_dashboard(request):
    # Get total vaccinations administered by the logged-in vet
    total_vaccinations = Vaccination.objects.filter(vet=request.user).count()
    treatment = Treatment.objects.filter(vet=request.user).count()

    # Get upcoming vaccinations due in the next 7 days
    upcoming_vaccinations = Vaccination.objects.filter(
        vet=request.user,
        next_due_date__gte=timezone.now(),
        next_due_date__lte=timezone.now() + timezone.timedelta(days=7)
    ).order_by("next_due_date")

    # Get total livestock handled by this vet
    total_livestock = Livestock.objects.filter(vaccination__vet=request.user).distinct().count()

    context = {
        "total_vaccinations": total_vaccinations,
        "upcoming_vaccinations": upcoming_vaccinations,
        "total_livestock": total_livestock,
        "treatment": treatment
    }

    return render(request, "vet/vet_dashboard.html", context)



from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

class VetTreatmentListView(LoginRequiredMixin, ListView):
    model = Treatment
    template_name = "vet/treatment_list.html"
    context_object_name = "treatments"

    def get_queryset(self):
        # Show treatments only for the logged-in vet
        return Treatment.objects.filter(vet=self.request.user).order_by("-treatment_date")


class VetTreatmentCreateView(LoginRequiredMixin, CreateView):
    model = Treatment
    template_name = "vet/treatment_form.html"
    fields = ["livestock", "treatment_date", "description", "medication", "cost"]
    success_url = reverse_lazy("vet_treatments")

    def form_valid(self, form):
        # Assign the logged-in vet automatically
        form.instance.vet = self.request.user
        return super().form_valid(form)
    


@login_required
def vaccination_list(request):
    """Display all vaccinations"""
    vaccinations = Vaccination.objects.select_related("livestock", "vet").order_by('-vaccination_date')
    return render(request, "vet/vaccination_list.html", {"vaccinations": vaccinations})


@login_required
def vaccination_create(request, livestock_id=None):
    """Create a vaccination record"""
    livestock = None
    if livestock_id:
        livestock = get_object_or_404(Livestock, id=livestock_id)

    if request.method == "POST":
        form = VaccinationForm(request.POST)
        if form.is_valid():
            vaccination = form.save(commit=False)
            vaccination.vet = request.user  # Assign the logged-in vet
            vaccination.save()
            messages.success(request, "Vaccination record added successfully.")
            return redirect("vaccination_list")
    else:
        form = VaccinationForm(initial={"livestock": livestock})

    return render(request, "vet/vaccination_form.html", {"form": form})