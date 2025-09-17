# # -*- encoding: utf-8 -*-
# """
# Copyright (c) 2019 - present AppSeed.us
# """

# from django.contrib import admin
# from django.urls import path, include  # add this

# urlpatterns = [
#     path('admin/', admin.site.urls),          # Django admin route
#     path("", include("apps.authentication.urls")), # Auth routes - login / register
#     path("", include("apps.home.urls"))             # UI Kits Html files
# ]

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.authentication.urls')),   # Login & Register
    path('', include('apps.home.urls')),             # Home dashboard
    path('', include('django.contrib.auth.urls')),   # Default auth URLs
    
]