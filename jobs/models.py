from django.db import models


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
    salary_range = models.CharField(max_length=100)
    is_remote = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} at {self.company}"
