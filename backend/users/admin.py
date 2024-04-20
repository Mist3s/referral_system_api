from django.contrib import admin

from .models import User, AuthCode


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'phone_number',
        'ref_code',
        'last_name',
        'first_name'
    )
    list_filter = ('phone_number',)
    search_fields = ('last_name', 'first_name', 'phone_number')


@admin.register(AuthCode)
class AuthCodeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'code',
        'user',
        'datetime_end',
        'used'
    )
