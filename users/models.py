from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import uuid
from datetime import timedelta


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


class EmailVerification(models.Model):
    """Model for email verification during registration"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Email verification for {self.user.username}"
    
    def is_expired(self, hours=24):
        """Check if verification token is expired"""
        return timezone.now() > self.created_at + timedelta(hours=hours)
    
    def send_verification_email(self):
        """Send verification email to user"""
        if self.is_verified:
            return False
        
        subject = 'Verify your JobRite account'
        html_message = render_to_string('users/emails/verification_email.html', {
            'user': self.user,
            'verification_url': f"{settings.SITE_URL}/users/verify-email/{self.token}/",
            'site_name': 'JobRite',
        })
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [self.user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Failed to send verification email: {e}")
            return False
    
    def verify_email(self):
        """Mark email as verified"""
        if not self.is_expired():
            self.is_verified = True
            self.verified_at = timezone.now()
            self.save()
            return True
        return False
