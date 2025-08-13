from django.contrib import admin
from .models import Job, JobApplication, SavedSearch, EmployerProfile


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'category', 'job_type', 'is_active', 'is_featured', 'is_remote', 'created_at')
    list_filter = ('category', 'job_type', 'is_active', 'is_featured', 'is_remote', 'created_at')
    search_fields = ('title', 'company', 'location', 'description')
    list_editable = ('is_active', 'is_featured', 'is_remote')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['title', 'company', 'location', 'category', 'job_type']
        }),
        ('Job Details', {
            'fields': ['description', 'requirements']
        }),
        ('Salary Information', {
            'fields': ['salary_range', 'salary_min', 'salary_max', 'salary_currency']
        }),
        ('Options', {
            'fields': ['is_remote', 'is_active', 'is_featured', 'application_deadline']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job', 'status', 'applied_at', 'has_cover_letter', 'has_resume')
    list_filter = ('status', 'applied_at', 'job__category', 'job__company')
    search_fields = ('applicant__username', 'applicant__email', 'job__title', 'job__company')
    list_editable = ('status',)
    ordering = ('-applied_at',)
    date_hierarchy = 'applied_at'
    readonly_fields = ('applied_at', 'updated_at')
    
    def has_cover_letter(self, obj):
        return bool(obj.cover_letter)
    has_cover_letter.boolean = True
    has_cover_letter.short_description = 'Cover Letter'
    
    def has_resume(self, obj):
        return bool(obj.resume)
    has_resume.boolean = True
    has_resume.short_description = 'Resume'
    
    fieldsets = (
        ('Application Info', {
            'fields': ('job', 'applicant', 'status')
        }),
        ('Application Content', {
            'fields': ('cover_letter', 'resume')
        }),
        ('Timestamps', {
            'fields': ('applied_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'query', 'location', 'category', 'email_alerts', 'created_at']
    list_filter = ['email_alerts', 'category', 'job_type', 'is_remote', 'created_at']
    search_fields = ['user__username', 'user__email', 'name', 'query', 'location']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'user', 'contact_email', 'company_size', 'is_verified', 'created_at']
    list_filter = ['company_size', 'is_verified', 'country', 'created_at']
    search_fields = ['company_name', 'user__username', 'user__email', 'contact_email']
    list_editable = ['is_verified']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = [
        ('Company Information', {
            'fields': ['user', 'company_name', 'company_description', 'company_website', 'company_logo', 'company_size']
        }),
        ('Contact Information', {
            'fields': ['contact_email', 'contact_phone']
        }),
        ('Address', {
            'fields': ['address_line1', 'address_line2', 'city', 'state_province', 'postal_code', 'country']
        }),
        ('Verification', {
            'fields': ['is_verified', 'verification_date']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
