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
    path('livestock.html', views.livestock_list, name='livestock'),
    path("vaccinations/", views.vaccination_list, name="vaccination_list"),


    path("vaccinations/", views.vaccination_list, name="vaccination_list"),
    path("vaccinations/add/", views.vaccination_create, name="vaccination_create"),
    path("vaccinations/add/<int:livestock_id>/", views.vaccination_create, name="vaccination_create_for_livestock"),


    # ✅ Catch-all for other HTML 
    
    path("vet/treatments/", VetTreatmentListView.as_view(), name="vet_treatments"),
    path("vet/treatments/add/", VetTreatmentCreateView.as_view(), name="add_treatment"),


    re_path(r'^.*\.*', views.pages, name='pages'),
]
