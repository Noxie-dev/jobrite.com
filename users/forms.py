from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information"""
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'location', 'skills', 'experience_level', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={
                'placeholder': 'Tell us about yourself...',
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'rows': 4,
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'City, State/Province, Country',
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
            }),
            'skills': forms.Textarea(attrs={
                'placeholder': 'List your key skills (e.g., Customer Service, Sales, Microsoft Office)',
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'rows': 3,
            }),
            'experience_level': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
                'accept': 'image/*',
            }),
        }
    
    def clean_bio(self):
        """Validate bio field"""
        bio = self.cleaned_data.get('bio', '').strip()
        if bio and len(bio) < 10:
            raise forms.ValidationError('Bio must be at least 10 characters long.')
        return bio
    
    def clean_location(self):
        """Validate location field"""
        location = self.cleaned_data.get('location', '').strip()
        if location and len(location) < 2:
            raise forms.ValidationError('Location must be at least 2 characters long.')
        return location
    
    def clean_skills(self):
        """Validate skills field"""
        skills = self.cleaned_data.get('skills', '').strip()
        if skills and len(skills) < 5:
            raise forms.ValidationError('Skills must be at least 5 characters long.')
        return skills
    
    def clean_profile_picture(self):
        """Validate profile picture upload"""
        picture = self.cleaned_data.get('profile_picture')
        if picture:
            if picture.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError('Profile picture must be smaller than 5MB.')
            
            # Check file type
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            if not any(picture.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError('Profile picture must be a JPG, PNG, or GIF file.')
        
        return picture

class UserRegistrationForm(UserCreationForm):
    """Extended user registration form"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'your.email@example.com',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'First Name',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Last Name',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Choose a username',
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
            }),
            'password1': forms.PasswordInput(attrs={
                'placeholder': 'Create a password',
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
            }),
            'password2': forms.PasswordInput(attrs={
                'placeholder': 'Confirm your password',
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
            }),
        }
    
    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email
    
    def save(self, commit=True):
        """Save user with additional fields"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.create(user=user)
        return user


class OnboardingForm(forms.ModelForm):
    """Multi-step onboarding form"""
    
    JOB_CATEGORIES = [
        ('call-center', 'Call Center'),
        ('customer-care', 'Customer Care'),
        ('sales', 'Sales'),
        ('hr', 'Human Resources'),
        ('it', 'IT Technician'),
        ('logistics', 'Logistics'),
        ('admin', 'Administrative'),
        ('other', 'Other'),
    ]
    
    LOCATION_CHOICES = [
        ('johannesburg', 'Johannesburg'),
        ('cape-town', 'Cape Town'),
        ('durban', 'Durban'),
        ('pretoria', 'Pretoria'),
        ('port-elizabeth', 'Port Elizabeth'),
        ('bloemfontein', 'Bloemfontein'),
        ('remote', 'Remote Work'),
        ('other', 'Other Location'),
    ]
    
    # Step 1: Personal Information
    bio = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Tell us about yourself, your career goals, and what makes you unique...',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
            'rows': 4,
        }),
        required=False,
        help_text='This will help employers understand your background and interests.'
    )
    
    profile_picture = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
            'accept': 'image/*',
        }),
        required=False,
        help_text='Upload a professional photo to make your profile stand out.'
    )
    
    # Step 2: Job Preferences
    preferred_job_categories = forms.MultipleChoiceField(
        choices=JOB_CATEGORIES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'grid grid-cols-2 gap-3',
        }),
        required=False,
        help_text='Select the job categories you\'re interested in.'
    )
    
    experience_level = forms.ChoiceField(
        choices=UserProfile.EXPERIENCE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'space-y-2',
        }),
        required=True,
        help_text='Select your current experience level.'
    )
    
    # Step 3: Location and Skills
    location = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'City, Province, Country',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
        }),
        required=False,
        help_text='Where are you located or willing to work?'
    )
    
    preferred_locations = forms.MultipleChoiceField(
        choices=LOCATION_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'grid grid-cols-2 gap-3',
        }),
        required=False,
        help_text='Select locations where you\'d like to work.'
    )
    
    skills = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'e.g., Customer Service, Microsoft Office, Sales, Communication, Problem Solving...',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
            'rows': 3,
        }),
        required=False,
        help_text='List your key skills and competencies.'
    )
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'experience_level', 'location', 'skills']
    
    def __init__(self, *args, **kwargs):
        self.step = kwargs.pop('step', '1')
        super().__init__(*args, **kwargs)
        
        # Show only relevant fields for each step
        if self.step == '1':
            # Personal Information
            self.fields = {k: v for k, v in self.fields.items() if k in ['bio', 'profile_picture']}
        elif self.step == '2':
            # Job Preferences
            self.fields = {k: v for k, v in self.fields.items() if k in ['preferred_job_categories', 'experience_level']}
        elif self.step == '3':
            # Location and Skills
            self.fields = {k: v for k, v in self.fields.items() if k in ['location', 'preferred_locations', 'skills']}
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Handle preferred categories and locations
        if 'preferred_job_categories' in self.cleaned_data:
            profile.preferred_job_categories = self.cleaned_data['preferred_job_categories']
        
        if 'preferred_locations' in self.cleaned_data:
            profile.preferred_locations = self.cleaned_data['preferred_locations']
        
        if commit:
            profile.save()
        return profile


class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form with styling"""
    
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
        }),
        help_text='We\'ll send you a link to reset your password.'
    )
    
    def clean_email(self):
        """Validate that the email exists in the system"""
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('No account found with this email address.')
        return email


class CustomSetPasswordForm(SetPasswordForm):
    """Custom set password form with styling"""
    
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your new password',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
        }),
        help_text='Your password must be at least 8 characters long and contain a mix of letters and numbers.'
    )
    
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your new password',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200',
        }),
        help_text='Enter the same password as before, for verification.'
    )