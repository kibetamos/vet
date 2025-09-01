from django.urls import path, re_path
from apps.home import views
from .views import * 
urlpatterns = [
    # ✅ Corrected homepage URL
    path('', views.index, name='home'),
#     path('', views.index, name='home'),
    # path('', views.index, name='home'),
    path('pages/<path:template>', views.pages, name='pages'),
    path('home/index/', views.admin_dashboard, name='admin_dashboard'),
    path('staff/staff/', views.staff_dashboard, name='staff_dashboard'),
    path('vet/vet/', views.vet_dashboard, name='vet_dashboard'),
    path('farmer/farmer/', views.farmer_dashboard, name='farmer_dashboard'),


    path('livestock/', views.livestock_list, name='livestock_list'),
     path('vet_livestock/', views.vet_livestock_list, name='vet_livestock_list'),
    path('livestock/edit/<int:pk>/', views.livestock_edit, name='livestock_edit'),
    path('livestock/delete/<int:pk>/', views.livestock_delete, name='livestock_delete'),
 



    # path('appointments/', views.Appointment.as_view(), name='appointments'),
    path('appointments/', views.AppointmentListView.as_view(), name='appointments'),

    path('vet/appointment/add/', views.AppointmentCreateView.as_view(), name='add_appointment'),
    path('vet/appointment/<int:pk>/edit/', views.AppointmentUpdateView.as_view(), name='edit_appointment'),
    path('vet/appointment/<int:pk>/delete/', views.AppointmentDeleteView.as_view(), name='delete_appointment'),

    path('farmer/treatments/', views.FarmerTreatmentListView.as_view(), name='farmer_treatments'),



    path("vaccinations/", views.vaccination_list, name="vaccination_list"),
    # path("vaccinations/add/", views.vaccination_create, name="vaccination_create"),
    # path("vaccinations/add/<int:livestock_id>/", views.vaccination_create, name="vaccination_create_for_livestock"),
    path('vet/vaccinations/add/', VaccinationCreateView.as_view(), name='add_vaccination'),
    path('vet/vaccination/<int:pk>/edit/', views.VaccinationUpdateView.as_view(), name='edit_vaccination'),
    path('vet/vaccination/<int:pk>/delete/', views.VaccinationDeleteView.as_view(), name='delete_vaccination'),


    # ✅ Catch-all for other HTML 
    
    path('vet/treatments/', views.VetTreatmentListView.as_view(), name='vet_treatments'),
    path('vet/treatment/add/', views.VetTreatmentCreateView.as_view(), name='add_treatment'),
    path('vet/treatment/<int:pk>/edit/', views.VetTreatmentUpdateView.as_view(), name='edit_treatment'),
    path('vet/treatment/<int:pk>/delete/', views.VetTreatmentDeleteView.as_view(), name='delete_treatment'),


    
    path("reports/farmer/", views.farmer_report, name="farmer_report"),
    path("reports/vet/", views.vet_report, name="vet_report"),

    re_path(r'^.*\.*', views.pages, name='pages'),
]
