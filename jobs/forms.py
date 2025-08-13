from django import forms
from .models import Job

class JobSearchForm(forms.Form):
    """Form for job search functionality"""
    
    q = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Job title, company, or keywords...',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
        }),
        label='Search Jobs'
    )
    
    location = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'City, state, or remote',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
        }),
        label='Location'
    )
    
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + Job.CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
        }),
        label='Category'
    )
    
    job_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Job.JOB_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
        }),
        label='Job Type'
    )
    
    def clean_q(self):
        """Validate search query"""
        query = self.cleaned_data.get('q', '').strip()
        if query and len(query) < 2:
            raise forms.ValidationError('Search query must be at least 2 characters long.')
        return query
    
    def clean_location(self):
        """Validate location input"""
        location = self.cleaned_data.get('location', '').strip()
        if location and len(location) < 2:
            raise forms.ValidationError('Location must be at least 2 characters long.')
        return location

class ContactForm(forms.Form):
    """Contact form for user inquiries"""
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Your full name',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
        }),
        label='Full Name'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'your.email@example.com',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
        }),
        label='Email Address'
    )
    
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'What is your inquiry about?',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
        }),
        label='Subject'
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Please describe your inquiry in detail...',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
            'rows': 5,
        }),
        label='Message'
    )
    
    def clean_name(self):
        """Validate name field"""
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError('Name must be at least 2 characters long.')
        if not name.replace(' ', '').isalpha():
            raise forms.ValidationError('Name should only contain letters and spaces.')
        return name
    
    def clean_message(self):
        """Validate message field"""
        message = self.cleaned_data.get('message', '').strip()
        if len(message) < 10:
            raise forms.ValidationError('Message must be at least 10 characters long.')
        return message