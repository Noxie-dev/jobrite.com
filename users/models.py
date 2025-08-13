from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    EXPERIENCE_CHOICES = [
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('executive', 'Executive Level'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    skills = models.TextField(blank=True)
    experience_level = models.CharField(max_length=50, choices=EXPERIENCE_CHOICES, default='entry')
    resume = models.FileField(upload_to='resumes/', blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True)
    
    # Onboarding fields
    onboarding_completed = models.BooleanField(default=False)
    preferred_job_categories = models.JSONField(default=list, blank=True)
    preferred_locations = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_preferred_categories_display(self):
        """Return a comma-separated string of preferred job categories"""
        if self.preferred_job_categories:
            return ', '.join(self.preferred_job_categories)
        return 'Not specified'
    
    def get_preferred_locations_display(self):
        """Return a comma-separated string of preferred locations"""
        if self.preferred_locations:
            return ', '.join(self.preferred_locations)
        return 'Not specified'
