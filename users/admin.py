from django.contrib import admin
from .models import UserProfile, EmailVerification


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'experience_level', 'onboarding_completed', 'created_at']
    list_filter = ['experience_level', 'onboarding_completed', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'location']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = [
        ('User Information', {
            'fields': ['user']
        }),
        ('Profile Details', {
            'fields': ['bio', 'location', 'skills', 'experience_level', 'resume', 'profile_picture']
        }),
        ('Onboarding', {
            'fields': ['onboarding_completed', 'preferred_job_categories', 'preferred_locations']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_email', 'is_verified', 'created_at', 'verified_at', 'is_expired_display']
    list_filter = ['is_verified', 'created_at', 'verified_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['token', 'created_at', 'verified_at']
    ordering = ['-created_at']
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email Address'
    
    def is_expired_display(self, obj):
        return obj.is_expired()
    is_expired_display.boolean = True
    is_expired_display.short_description = 'Is Expired'
    
    fieldsets = [
        ('User Information', {
            'fields': ['user']
        }),
        ('Verification Details', {
            'fields': ['token', 'is_verified', 'created_at', 'verified_at']
        })
    ]
