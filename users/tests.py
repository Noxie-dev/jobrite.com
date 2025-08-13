from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import UserProfileForm, UserRegistrationForm

class UsersViewsTestCase(TestCase):
    """Test cases for users app views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            bio='Test bio',
            location='Test City',
            skills='Python, Django, Testing',
            experience_level='mid'
        )
    
    def test_profile_page_requires_login(self):
        """Test profile page requires authentication"""
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_profile_page_loads_when_authenticated(self):
        """Test profile page loads for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')

class UsersFormsTestCase(TestCase):
    """Test cases for users app forms"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
    
    def test_user_profile_form_validation(self):
        """Test user profile form validation"""
        # Valid form
        form_data = {
            'bio': 'This is a valid bio with enough characters.',
            'location': 'New York, NY',
            'skills': 'Python, Django, JavaScript',
            'experience_level': 'mid'
        }
        form = UserProfileForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Invalid form
        invalid_data = {
            'bio': 'Short',
            'location': 'A',
            'skills': 'JS',
            'experience_level': 'senior'
        }
        form = UserProfileForm(data=invalid_data)
        self.assertFalse(form.is_valid())
    
    def test_user_registration_form_validation(self):
        """Test user registration form validation"""
        # Valid form
        form_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test duplicate email
        form_data['email'] = 'existing@example.com'
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('A user with this email already exists.', form.errors['email'])
