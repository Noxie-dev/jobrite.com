from django import forms
from .models import Job, JobApplication, SavedSearch, EmployerProfile
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

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
    
    # Advanced filters
    salary_min = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Minimum salary',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
            'min': '0',
        }),
        label='Minimum Salary'
    )
    
    salary_max = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Maximum salary',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
            'min': '0',
        }),
        label='Maximum Salary'
    )
    
    is_remote = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-accent bg-gray-100 border-gray-300 rounded focus:ring-accent focus:ring-2',
        }),
        label='Remote work only'
    )
    
    date_posted = forms.ChoiceField(
        choices=SavedSearch.DATE_POSTED_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
        }),
        label='Date Posted'
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
    
    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')
        
        if salary_min and salary_max and salary_min > salary_max:
            raise forms.ValidationError('Minimum salary cannot be greater than maximum salary.')
        
        return cleaned_data

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


class JobApplicationForm(forms.ModelForm):
    """Form for job applications"""
    
    class Meta:
        model = JobApplication
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'placeholder': 'Tell us why you\'re interested in this position and what makes you a great fit...',
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'rows': 6,
            }),
            'resume': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'accept': '.pdf,.doc,.docx',
            }),
        }
        labels = {
            'cover_letter': 'Cover Letter (Optional)',
            'resume': 'Resume (Optional if already in profile)',
        }
    
    def clean_resume(self):
        """Validate resume file"""
        resume = self.cleaned_data.get('resume')
        if resume:
            # Check file size (5MB limit)
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Resume file size must be less than 5MB.')
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx']
            file_extension = resume.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError('Resume must be a PDF, DOC, or DOCX file.')
        
        return resume
    
    def clean_cover_letter(self):
        """Validate cover letter"""
        cover_letter = self.cleaned_data.get('cover_letter', '').strip()
        if cover_letter and len(cover_letter) < 50:
            raise forms.ValidationError('Cover letter must be at least 50 characters long if provided.')
        return cover_letter


class SavedSearchForm(forms.ModelForm):
    """Form for saving search criteria"""
    
    class Meta:
        model = SavedSearch
        fields = ['name', 'email_alerts']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Give this search a name...',
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'maxlength': '100',
            }),
            'email_alerts': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-accent bg-gray-100 border-gray-300 rounded focus:ring-accent focus:ring-2',
            }),
        }
        labels = {
            'name': 'Search Name',
            'email_alerts': 'Send me email alerts for new jobs matching this search',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_name(self):
        """Validate search name is unique for this user"""
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError('Search name must be at least 2 characters long.')
        
        if self.user:
            existing_search = SavedSearch.objects.filter(user=self.user, name=name)
            if self.instance.pk:
                existing_search = existing_search.exclude(pk=self.instance.pk)
            
            if existing_search.exists():
                raise forms.ValidationError('You already have a saved search with this name.')
        
        return name


class EmployerProfileForm(forms.ModelForm):
    """Form for employer profile creation/editing"""
    
    class Meta:
        model = EmployerProfile
        exclude = ['user', 'is_verified', 'verification_date']
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'placeholder': 'Company Name',
            }),
            'company_description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'placeholder': 'Brief description of your company...',
                'rows': 4,
            }),
            'company_website': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'placeholder': 'https://www.example.com',
            }),
            'company_size': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'placeholder': 'contact@company.com',
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'placeholder': '+1 (555) 123-4567',
            }),
            'address_line1': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'placeholder': '123 Main Street',
            }),
            'address_line2': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'placeholder': 'Suite 100 (optional)',
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'placeholder': 'City',
            }),
            'state_province': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'placeholder': 'State/Province',
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'placeholder': '12345',
            }),
            'country': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'placeholder': 'Country',
            }),
            'company_logo': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'accept': 'image/*',
            }),
        }
    
    def clean_company_logo(self):
        """Validate company logo"""
        logo = self.cleaned_data.get('company_logo')
        if logo:
            # Check file size (2MB limit)
            if logo.size > 2 * 1024 * 1024:
                raise forms.ValidationError('Company logo must be less than 2MB.')
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if logo.content_type not in allowed_types:
                raise forms.ValidationError('Company logo must be a JPEG, PNG, or GIF image.')
        
        return logo


class JobPostingForm(forms.ModelForm):
    """Form for employers to post jobs"""
    
    class Meta:
        model = Job
        exclude = ['is_featured', 'created_at', 'updated_at']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'placeholder': 'Job Title',
            }),
            'company': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'placeholder': 'Company Name',
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'placeholder': 'Job Location',
            }),
            'job_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'placeholder': 'Detailed job description...',
                'rows': 6,
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'placeholder': 'Job requirements and qualifications...',
                'rows': 4,
            }),
            'salary_range': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'placeholder': 'e.g., $50,000 - $70,000 per year',
            }),
            'salary_min': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'placeholder': 'Minimum salary',
                'min': '0',
            }),
            'salary_max': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'placeholder': 'Maximum salary',
                'min': '0',
            }),
            'salary_currency': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'placeholder': 'USD',
                'maxlength': '3',
            }),
            'is_remote': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-accent bg-gray-100 border-gray-300 rounded focus:ring-accent focus:ring-2',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-accent bg-gray-100 border-gray-300 rounded focus:ring-accent focus:ring-2',
            }),
            'application_deadline': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'type': 'datetime-local',
            }),
        }
        labels = {
            'is_remote': 'This is a remote position',
            'is_active': 'Accept applications for this job',
            'application_deadline': 'Application Deadline (optional)',
        }
    
    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')
        application_deadline = cleaned_data.get('application_deadline')
        
        if salary_min and salary_max and salary_min > salary_max:
            raise forms.ValidationError('Minimum salary cannot be greater than maximum salary.')
        
        if application_deadline and application_deadline < timezone.now():
            raise forms.ValidationError('Application deadline cannot be in the past.')
        
        return cleaned_data
