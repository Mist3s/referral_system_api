from django.contrib import admin

from .models import Referral


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'referral'
    )
    list_filter = ('user',)
    search_fields = ('user', 'referral')
