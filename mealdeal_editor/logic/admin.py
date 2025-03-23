from django.contrib import admin
from .models import InvitationCode
import random
import string

def generate_random_code(length=10):
    """Generate a random alphanumeric code of specified length"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def create_bulk_invitation_codes(modeladmin, request, queryset):
    """Admin action to create multiple invitation codes"""
    num_codes = 10  # You can modify this or make it configurable
    for _ in range(num_codes):
        code = generate_random_code()
        InvitationCode.objects.create(code=code)
    modeladmin.message_user(request, f"{num_codes} new invitation codes created successfully")

create_bulk_invitation_codes.short_description = "Create 10 random invitation codes"

class InvitationCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'is_used', 'created_at', 'used_at', 'used_by')
    list_filter = ('is_used', 'created_at', 'used_at')
    search_fields = ('code', 'used_by')
    readonly_fields = ('created_at',)
    actions = [create_bulk_invitation_codes]
    fieldsets = (
        (None, {
            'fields': ('code', 'is_used')
        }),
        ('Usage Information', {
            'fields': ('created_at', 'used_at', 'used_by'),
            'classes': ('collapse',)
        }),
    )

admin.site.register(InvitationCode, InvitationCodeAdmin)
