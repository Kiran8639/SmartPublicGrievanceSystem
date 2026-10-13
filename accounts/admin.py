from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Department, Complaint

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
    'username',
    'first_name',
    'last_name',
    'email',
    'role',
    'department',
    'is_staff',
    'is_active'
    )


    list_filter = (
        'role',
        'department',
        'is_staff',
        'is_active'
    )

    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email'
    )

    ordering = ('username',)

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': ('role', 'department')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Information', {
            'fields': ('role', 'department')
        }),
    )


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
    'title',
    'citizen',
    'department',
    'assigned_staff',
    'priority',
    'status',
    'created_at'
    )


    list_filter = (
        'status',
        'priority',
        'department',
        'created_at'
    )

    search_fields = (
        'title',
        'description',
        'location',
        'citizen__username',
        'department__name'
    )

    ordering = ('-created_at',)
    list_per_page = 20
    date_hierarchy = 'created_at'

