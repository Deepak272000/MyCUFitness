from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from .models import User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("email", "role", "is_active", "is_superuser")
    list_filter = ("role", "is_active", "is_superuser")
    readonly_fields = ("last_login",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("role", "fitness_goals", "dietary_preferences", "allergies")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "role", "is_staff", "is_active"),
        }),
    )

    search_fields = ("email",)
    ordering = ("email",)
    filter_horizontal = ("groups", "user_permissions")

    def get_fieldsets(self, request, obj=None):
        """ Ensure the correct fieldset is used when adding a new user """
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)
admin.site.register(User, CustomUserAdmin)
from django.contrib import admin
from .models import Review

admin.site.register(Review)  # ✅ Now you can see reviews in Django Admin
