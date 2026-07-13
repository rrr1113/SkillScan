from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User

# Register your models here.

class UserAdmin(BaseUserAdmin):
    model = User

    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('profile_photo', 'phone_number')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('profile_photo', 'phone_number')}),
    )

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser


admin.site.register(User, UserAdmin)