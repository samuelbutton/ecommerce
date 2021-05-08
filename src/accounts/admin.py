from django.contrib import admin

from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .models import GuestEmail
from .forms import UserAdminCreationForm, UserAdminChangeForm

User = get_user_model()


class UserAdmin(admin.ModelAdmin):

    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    list_display = ("email", "admin",)
    list_filter = ("admin", "staff", "active",)

    fieldsets = (
        (None, {"fields": ("email", "password",)}),
        ("Personal Info", {"fields": ("full_name",)}),
        ("Permissions", {"fields": ("admin", "staff", "active",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2",)}
         )
    )

    search_fields = ("email", "full_name",)
    ordering = ("email",)
    filter_horizontal = ()

    # class Meta:
    #     model = User


admin.site.register(User, UserAdmin)


class GuestEmailAdmin(admin.ModelAdmin):
    search_fields = ["email"]

    class Meta:
        model = GuestEmail


admin.site.register(GuestEmail)
