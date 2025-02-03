from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("email", "role", "is_staff", "is_active", "is_superuser")
    list_filter = ("role", "is_staff", "is_active", "is_superuser")
    readonly_fields = (
        "last_login",
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("role", "fitness_goals", "dietary_preferences", "allergies")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "role", "is_staff", "is_active"),
        }),
    )
    search_fields = ("email",)
    ordering = ("email",)  # ✅ FIX: Change 'username' → 'email'

admin.site.register(User, CustomUserAdmin)
