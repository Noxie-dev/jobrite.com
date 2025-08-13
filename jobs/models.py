from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('remote', 'Remote'),
        ('contract', 'Contract'),
    ]
    
    CATEGORY_CHOICES = [
        ('call-center', 'Call Center'),
        ('customer-care', 'Customer Care'),
        ('sales', 'Sales'),
        ('hr', 'Human Resources'),
        ('it', 'IT Technician'),
        ('logistics', 'Logistics'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    requirements = models.TextField()
    salary_range = models.CharField(max_length=100)  # Keep for backward compatibility
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Minimum salary in local currency")
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Maximum salary in local currency")
    salary_currency = models.CharField(max_length=3, default='USD', help_text="Currency code (USD, EUR, etc.)")
    is_remote = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, help_text="Whether this job is actively accepting applications")
    application_deadline = models.DateTimeField(null=True, blank=True, help_text="Application deadline")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} at {self.company}"
    
    def is_recently_posted(self, days=7):
        """Check if job was posted within the last N days"""
        return self.created_at >= timezone.now() - timedelta(days=days)
    
    def get_salary_display(self):
        """Return formatted salary range"""
        if self.salary_min and self.salary_max:
            return f"{self.salary_currency} {self.salary_min:,.0f} - {self.salary_max:,.0f}"
        elif self.salary_min:
            return f"{self.salary_currency} {self.salary_min:,.0f}+"
        elif self.salary_range:
            return self.salary_range
        return "Not specified"


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewing', 'Under Review'),
        ('interview', 'Interview Scheduled'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    cover_letter = models.TextField(blank=True, help_text="Optional cover letter")
    resume = models.FileField(upload_to='applications/resumes/', blank=True, help_text="Upload your resume (optional if already in profile)")
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('job', 'applicant')  # Prevent duplicate applications
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.applicant.get_full_name() or self.applicant.username} - {self.job.title}"
    
    def get_status_display_class(self):
        """Return CSS class for status display"""
        status_classes = {
            'pending': 'bg-yellow-100 text-yellow-800',
            'reviewing': 'bg-blue-100 text-blue-800',
            'interview': 'bg-purple-100 text-purple-800',
            'accepted': 'bg-green-100 text-green-800',
            'rejected': 'bg-red-100 text-red-800',
            'withdrawn': 'bg-gray-100 text-gray-800',
        }
        return status_classes.get(self.status, 'bg-gray-100 text-gray-800')


class SavedSearch(models.Model):
    """Model for saving user search criteria"""
    
    DATE_POSTED_CHOICES = [
        ('', 'Any time'),
        ('1', 'Past 24 hours'),
        ('3', 'Past 3 days'),
        ('7', 'Past week'),
        ('14', 'Past 2 weeks'),
        ('30', 'Past month'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_searches')
    name = models.CharField(max_length=100, help_text="Name for this saved search")
    
    # Search criteria fields
    query = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=50, blank=True)
    job_type = models.CharField(max_length=50, blank=True)
    
    # Advanced filters
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_remote = models.BooleanField(null=True, blank=True)
    date_posted = models.CharField(max_length=2, choices=DATE_POSTED_CHOICES, blank=True)
    
    # Email alerts
    email_alerts = models.BooleanField(default=False, help_text="Send email alerts for new jobs matching this search")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'name')  # User can't have duplicate search names
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    def get_search_url(self):
        """Generate URL for this saved search"""
        from django.urls import reverse
        from urllib.parse import urlencode
        
        params = {}
        if self.query: params['q'] = self.query
        if self.location: params['location'] = self.location
        if self.category: params['category'] = self.category
        if self.job_type: params['job_type'] = self.job_type
        if self.salary_min: params['salary_min'] = str(self.salary_min)
        if self.salary_max: params['salary_max'] = str(self.salary_max)
        if self.is_remote is not None: params['is_remote'] = 'on' if self.is_remote else ''
        if self.date_posted: params['date_posted'] = self.date_posted
        
        base_url = reverse('jobs:search')
        if params:
            return f"{base_url}?{urlencode(params)}"
        return base_url


class EmployerProfile(models.Model):
    """Profile for employers who can post jobs"""
    
    COMPANY_SIZE_CHOICES = [
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('501-1000', '501-1000 employees'),
        ('1000+', '1000+ employees'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    company_name = models.CharField(max_length=200)
    company_description = models.TextField()
    company_website = models.URLField(blank=True)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True)
    company_size = models.CharField(max_length=20, choices=COMPANY_SIZE_CHOICES)
    
    # Contact information
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True)
    
    # Address
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='United States')
    
    # Verification and approval
    is_verified = models.BooleanField(default=False, help_text="Whether the employer has been verified")
    verification_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.company_name} - {self.user.get_full_name() or self.user.username}"
    
    def get_full_address(self):
        """Return formatted full address"""
        address_parts = [self.address_line1]
        if self.address_line2:
            address_parts.append(self.address_line2)
        address_parts.extend([f"{self.city}, {self.state_province} {self.postal_code}", self.country])
        return "\n".join(address_parts)
