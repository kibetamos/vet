from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Livestock, Appointment, Treatment, Vaccination, Report

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'user_picture')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'user_picture')}),
    )
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Livestock)
admin.site.register(Appointment)
admin.site.register(Treatment)
admin.site.register(Vaccination)
admin.site.register(Report)
