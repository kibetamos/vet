
from django.http import Http404
from django.contrib import messages
from django.utils import timezone
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from apps.home.models import Vaccination, Treatment, Appointment
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from apps.home.forms import VaccinationForm
from apps.home.models import *
from .forms import *
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.home.models import *
from django.db.models import Count

# @login_required(login_url="/login/")
# def index(request):
#     context = {'segment': 'index'}

#     html_template = loader.get_template('home/index.html')
#     return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
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


class AppointmentListView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = "vet/appointments.html"
    context_object_name = "appointments"
    ordering = ['-date']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Check if user is a vet or has staff permissions
        if self.request.user.is_staff or getattr(self.request.user, "role", "") == "vet":
            return queryset  # Show all appointments
        
        # Otherwise, filter for farmer appointments only
        return queryset.filter(farmer=self.request.user)


# class AppointmentCreateView(LoginRequiredMixin, CreateView):
#     model = Appointment
#     form_class = AppointmentForm
#     template_name = "vet/appointment_form.html"
#     success_url = reverse_lazy("appointments")
class AppointmentCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = "vet/appointment_form.html"
    success_url = reverse_lazy("appointments")

    def get_form_kwargs(self):
        """Pass the current user to the form so we can filter livestock."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)

        # If the logged-in user is a farmer, hide farmer field & prefill it
        if getattr(self.request.user, "role", "") == "farmer":
            form.fields["farmer"].widget = forms.HiddenInput()
            form.fields["farmer"].initial = self.request.user

        return form

    def form_valid(self, form):
        """Ensure farmer is set automatically for farmers."""
        if getattr(self.request.user, "role", "") == "farmer":
            form.instance.farmer = self.request.user
        return super().form_valid(form)

    def form_valid(self, form):
        # For farmers, force the logged-in user as the farmer
        if getattr(self.request.user, "role", "") == "farmer":
            form.instance.farmer = self.request.user
        return super().form_valid(form)

class AppointmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = "vet/appointment_form.html"
    success_url = reverse_lazy("appointments")

    def get_object(self, queryset=None):
        """Restrict farmers to editing only their own appointments."""
        obj = super().get_object(queryset)
        if getattr(self.request.user, "role", "") == "farmer" and obj.farmer != self.request.user:
            raise Http404("You are not allowed to edit this appointment.")
        return obj

    def get_form_kwargs(self):
        """Pass current user to the form to filter livestock."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)

        # If farmer is editing, hide farmer field and lock it to their account
        if getattr(self.request.user, "role", "") == "farmer":
            form.fields["farmer"].widget = forms.HiddenInput()
            form.fields["farmer"].initial = self.request.user

        return form

class AppointmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Appointment
    template_name = "vet/appointment_confirm_delete.html"
    success_url = reverse_lazy("appointments")

    def get_object(self, queryset=None):
        """Restrict farmers from deleting other farmers' appointments."""
        obj = super().get_object(queryset)
        if getattr(self.request.user, "role", "") == "farmer" and obj.farmer != self.request.user:
            raise Http404("You are not allowed to delete this appointment.")
        return obj


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


from django.utils.timezone import now

@login_required(login_url="/login/")
def farmer_dashboard(request):
    user = request.user

    # Determine which livestock to show based on role
    if user.role == 'admin':
        livestock_qs = Livestock.objects.all()
    elif user.role == 'vet':
        livestock_qs = Livestock.objects.all()
    elif user.role == 'farmer':
        livestock_qs = Livestock.objects.filter(farmer=user)
    else:
        return render(request, "home/page-403.html")

    # Count livestock types
    # livestock_counts = livestock_qs.values("livestock_type").annotate(total=Count("id"))
    cattle_list = livestock_qs.filter(livestock_type='cattle')
    livestock_counts = (livestock_qs.values("livestock_type").annotate(total=Count("id")))
    
    recent_vaccinations = Vaccination.objects.filter(
            livestock__farmer=user
        ).order_by("-vaccination_date")[:5]
    # Prepare health status per animal
    livestock_list = []
    for animal in livestock_qs:
        due_vaccinations = animal.vaccination_set.filter(next_due_date__lte=now()).exists()
        livestock_list.append({
            "name": animal.name,
            "type": animal.livestock_type,
            "weight": animal.weight,
            "breed": animal.breed,
            "health_status": "Vaccination due" if due_vaccinations else "Healthy",
        })
        
    recent_treatments = Treatment.objects.filter(
        livestock__farmer=user
    ).order_by("-treatment_date")[:5]
    context = {
        # "total_livestock": livestock_qs.count(),
        
        "cattle_list": cattle_list,
        "total_livestock": livestock_qs.count(),
        "total_cattle": next((x["total"] for x in livestock_counts if x["livestock_type"] == "cattle"), 0),
        "total_sheep": next((x["total"] for x in livestock_counts if x["livestock_type"] == "sheep"), 0),
        "total_goats": next((x["total"] for x in livestock_counts if x["livestock_type"] == "goat"), 0),
        "total_poultry": next((x["total"] for x in livestock_counts if x["livestock_type"] == "poultry"), 0),
        "total_other": next((x["total"] for x in livestock_counts if x["livestock_type"] == "other"), 0),
        "livestock_list": livestock_list,
        "recent_vaccinations": recent_vaccinations,
        "recent_treatments":recent_treatments,
    }

    return render(request, "farmer/farmer_dashboard.html", context)


class FarmerTreatmentListView(LoginRequiredMixin, ListView):
    model = Treatment
    template_name = 'farmer/farmer_treatment_list.html'  # Create this template
    context_object_name = 'treatments'

    def get_queryset(self):
        # Only show treatments for livestock that belongs to the logged-in farmer
        return Treatment.objects.filter(livestock__farmer=self.request.user).order_by('-treatment_date')


# @login_required(login_url="/login/")
# def farmer_dashboard(request):
#     user = request.user

#     # Determine which livestock to show based on role
#     if user.role == 'admin':
#         livestock_qs = Livestock.objects.all()
#     elif user.role == 'vet':
#         # If you later add an assigned_vet field, replace this
#         livestock_qs = Livestock.objects.all()
#     elif user.role == 'farmer':
#         livestock_qs = Livestock.objects.filter(farmer=user)
#     else:
#         # Unknown role → deny access
#         return render(request, "home/page-403.html")

#     # Get counts efficiently in one DB query
#     livestock_counts = (livestock_qs.values("livestock_type").annotate(total=Count("id")))
#     recent_vaccinations = Vaccination.objects.filter(
#             livestock__farmer=user
#         ).order_by("-vaccination_date")[:5]
#     # Prepare context
#     context = {
#         "total_livestock": livestock_qs.count(),
#         "total_cattle": next((x["total"] for x in livestock_counts if x["livestock_type"] == "cattle"), 0),
#         "total_sheep": next((x["total"] for x in livestock_counts if x["livestock_type"] == "sheep"), 0),
#         "total_goats": next((x["total"] for x in livestock_counts if x["livestock_type"] == "goat"), 0),
#         "total_poultry": next((x["total"] for x in livestock_counts if x["livestock_type"] == "poultry"), 0),
#         "total_other": next((x["total"] for x in livestock_counts if x["livestock_type"] == "other"), 0),
#         "recent_vaccinations": recent_vaccinations,
#     }

#     return render(request, "farmer/farmer_dashboard.html", context)
# //livestock
@login_required
def livestock_list(request):
    user = request.user

    # Determine which livestock to show based on role
    if user.role in ['admin', 'vet']:
        livestock = Livestock.objects.all()
    elif user.role == 'farmer':
        livestock = Livestock.objects.filter(farmer=user)
    else:
        livestock = Livestock.objects.none()  # no access for other roles

    if request.method == "POST":
        form = LivestockForm(request.POST)
        if form.is_valid():
            livestock_instance = form.save(commit=False)
            
            # Only set farmer automatically if user is a farmer
            if user.role == 'farmer':
                livestock_instance.farmer = user
            
            livestock_instance.save()
            messages.success(request, "Livestock added successfully!")
            return redirect('livestock_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LivestockForm()

    return render(request, 'farmer/livestock.html', {
        'livestock': livestock,
        'form': form,
    })

@login_required
def vet_livestock_list(request):
    user = request.user

    # Determine which livestock to show based on role
    if user.role in ['admin', 'vet']:
        livestock = Livestock.objects.all()
    elif user.role == 'farmer':
        livestock = Livestock.objects.filter(farmer=user)
    else:
        livestock = Livestock.objects.none()  # no access for other roles

    if request.method == "POST":
        form = LivestockForm(request.POST)
        if form.is_valid():
            livestock_instance = form.save(commit=False)
            
            # Only set farmer automatically if user is a farmer
            if user.role == 'farmer':
                livestock_instance.farmer = user
            
            livestock_instance.save()
            messages.success(request, "Livestock added successfully!")
            return redirect('livestock_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LivestockForm()

    return render(request, 'vet/livestock.html', {
        'livestock': livestock,
        'form': form,
    })

@login_required
def livestock_edit(request, pk):
    livestock_instance = get_object_or_404(Livestock, pk=pk, farmer=request.user)

    if request.method == "POST":
        form = LivestockForm(request.POST, instance=livestock_instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Livestock updated successfully!")
            return redirect('livestock_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LivestockForm(instance=livestock_instance)

    return render(request, 'farmer/livestock_edit.html', {'form': form})


@login_required
def livestock_delete(request, pk):
    livestock_instance = get_object_or_404(Livestock, pk=pk, farmer=request.user)

    if request.method == "POST":
        livestock_instance.delete()
        messages.success(request, "Livestock deleted successfully!")
        return redirect('livestock_list')

    return render(request, 'farmer/livestock_delete.html', {'livestock': livestock_instance})




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


# @login_required
# def vet_dashboard(request):
#     # Get total vaccinations administered by the logged-in vet
#     total_vaccinations = Vaccination.objects.filter(vet=request.user).count()
#     total_treatments = Treatment.objects.filter(vet=request.user).count()
#     # total_appointments = Appointment.objects.filter(vet=request.user).count()

#     # Get upcoming vaccinations due in the next 7 days
#     upcoming_vaccinations = Vaccination.objects.filter(
#         vet=request.user,
#         next_due_date__gte=timezone.now(),
#         next_due_date__lte=timezone.now() + timezone.timedelta(days=7)
#     ).order_by("next_due_date")

#     # Get total livestock handled by this vet
#     total_livestock = Livestock.objects.filter(vaccination__vet=request.user).distinct().count()

#     context = {
#         "total_vaccinations": total_vaccinations,
#         "total_treatments": total_treatments,
#         # "total_appointments": total_appointments,
#         "upcoming_vaccinations": upcoming_vaccinations,
#         "total_livestock": total_livestock,
#     }

#     return render(request, "vet/vet_dashboard.html", context)

@login_required(login_url="/login/")
def vet_dashboard(request):
    user = request.user

    if user.role != "vet":
        return render(request, "home/page-403.html")

    # Show all livestock
    livestock_qs = Livestock.objects.all()

    # Count livestock types
    livestock_counts = livestock_qs.values("livestock_type").annotate(total=Count("id"))

    # Total stats
    total_vaccinations = Vaccination.objects.count()
    total_treatments = Treatment.objects.count()
    total_appointments = Appointment.objects.count()

    # Prepare health status for all livestock
    livestock_list = []
    for animal in livestock_qs:
        due_vaccinations = animal.vaccination_set.filter(next_due_date__lte=now()).exists()
        livestock_list.append({
            "name": animal.name,
            "type": animal.livestock_type,
            "weight": animal.weight,
            "breed": animal.breed,
            "health_status": "Vaccination due" if due_vaccinations else "Healthy",
        })

    recent_vaccinations = Vaccination.objects.all().order_by("-vaccination_date")[:5]
    recent_treatments = Treatment.objects.all().order_by("-treatment_date")[:5]
    recent_appointments = Appointment.objects.all().order_by("-date")[:5]

    context = {
        "total_livestock": livestock_qs.count(),
        "total_vaccinations": total_vaccinations,
        "total_treatments": total_treatments,
        "total_appointments": total_appointments,
        "livestock_list": livestock_list,
        "recent_vaccinations": recent_vaccinations,
        "recent_treatments": recent_treatments,
        "recent_appointments": recent_appointments,
        "total_cattle": next((x["total"] for x in livestock_counts if x["livestock_type"] == "cattle"), 0),
        "total_sheep": next((x["total"] for x in livestock_counts if x["livestock_type"] == "sheep"), 0),
        "total_goats": next((x["total"] for x in livestock_counts if x["livestock_type"] == "goat"), 0),
        "total_poultry": next((x["total"] for x in livestock_counts if x["livestock_type"] == "poultry"), 0),
        "total_other": next((x["total"] for x in livestock_counts if x["livestock_type"] == "other"), 0),
    }

    return render(request, "vet/vet_dashboard.html", context)



class VetTreatmentListView(LoginRequiredMixin, ListView):
    model = Treatment
    template_name = "vet/treatment_list.html"
    context_object_name = "treatments"

    def get_queryset(self):
        # Show treatments only for the logged-in vet
        return Treatment.objects.filter(vet=self.request.user).order_by("-treatment_date")


class VetTreatmentCreateView(LoginRequiredMixin, CreateView):
    model = Treatment
    form_class = TreatmentForm  # Use the form from forms.py
    template_name = "vet/treatment_form.html"
    success_url = reverse_lazy("vet_treatments")

    def form_valid(self, form):
        # Assign the logged-in vet automatically
        form.instance.vet = self.request.user
        return super().form_valid(form)
    
class VetTreatmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Treatment
    form_class = TreatmentForm
    template_name = "vet/treatment_form.html"
    success_url = reverse_lazy("vet_treatments")

class VetTreatmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Treatment
    template_name = "vet/treatment_confirm_delete.html"
    success_url = reverse_lazy("vet_treatments")    


@login_required
def vaccination_list(request):
    user = request.user

    # If admin or staff → show all vaccinations
    if user.is_staff or user.role == "admin" or user.role == "staff":
        vaccinations = Vaccination.objects.all()

    # If vet → show vaccinations assigned to them
    elif user.role == "vet":
        vaccinations = Vaccination.objects.filter(vet=user)

    # Otherwise, assume farmer → show vaccinations for farmer's livestock only
    else:
        vaccinations = Vaccination.objects.filter(livestock__farmer=user)

    # Show "Add Vaccination" button only for vet, admin, and staff
    show_add_button = (
        user.is_staff
        or user.role == "vet"
        or user.role == "admin"
        or user.role == "staff"
    )

    return render(
        request,
        "vet/vaccination_list.html",
        {
            "vaccinations": vaccinations,
            "show_add_button": show_add_button,
        },
    )

class VaccinationCreateView(LoginRequiredMixin, CreateView):
    model = Vaccination
    form_class = VaccinationForm
    template_name = "vet/vaccination_form.html"
    success_url = reverse_lazy("vaccination_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # Pass logged-in user to form
        return kwargs

    def form_valid(self, form):
        # Assign the logged-in vet automatically
        form.instance.vet = self.request.user
        return super().form_valid(form)
   

class VaccinationUpdateView(LoginRequiredMixin, UpdateView):
    model = Vaccination
    form_class = VaccinationForm
    template_name = "vet/vaccination_form.html"
    success_url = reverse_lazy("vaccination_list")

class VaccinationDeleteView(LoginRequiredMixin, DeleteView):
    model = Vaccination
    template_name = "vet/vaccination_confirm_delete.html"
    success_url = reverse_lazy("vaccination_list")

