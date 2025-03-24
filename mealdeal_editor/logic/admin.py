from django.contrib import admin
from .models import InvitationCode, PartnerApplication, Contact
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

class PartnerApplicationAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'business_type', 'city', 'contact_name', 'email', 'status', 'created_at')
    list_filter = ('status', 'business_type', 'city', 'created_at')
    search_fields = ('business_name', 'contact_name', 'email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Business Information', {
            'fields': ('business_name', 'business_type', 'address', 'city', 'status')
        }),
        ('Contact Information', {
            'fields': ('contact_name', 'email', 'phone_number')
        }),
        ('Online Presence', {
            'fields': ('website_url', 'instagram_url'),
        }),
        ('Additional Information', {
            'fields': ('additional_info',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_applications', 'reject_applications']
    
    def approve_applications(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f"{updated} application(s) have been approved.")
    approve_applications.short_description = "Mark selected applications as approved"
    
    def reject_applications(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f"{updated} application(s) have been rejected.")
    reject_applications.short_description = "Mark selected applications as rejected"

class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email')
        }),
        ('Message Details', {
            'fields': ('subject', 'message')
        }),
        ('Admin Section', {
            'fields': ('status', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_in_progress', 'mark_as_resolved']
    
    def mark_as_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress')
        self.message_user(request, f"{updated} contact request(s) marked as in progress.")
    mark_as_in_progress.short_description = "Mark selected contacts as in progress"
    
    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(status='resolved')
        self.message_user(request, f"{updated} contact request(s) marked as resolved.")
    mark_as_resolved.short_description = "Mark selected contacts as resolved"

admin.site.register(InvitationCode, InvitationCodeAdmin)
admin.site.register(PartnerApplication, PartnerApplicationAdmin)
admin.site.register(Contact, ContactAdmin)
