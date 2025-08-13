from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Job
from .forms import JobSearchForm, ContactForm

class JobsViewsTestCase(TestCase):
    """Test cases for jobs app views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test jobs
        self.job1 = Job.objects.create(
            title='Software Developer',
            company='Tech Corp',
            location='Remote',
            job_type='full-time',
            category='it',
            description='Great opportunity for developers',
            requirements='Python, Django experience',
            salary_range='$50,000 - $70,000',
            is_remote=True,
            is_featured=True
        )
        
        self.job2 = Job.objects.create(
            title='Customer Service Representative',
            company='Service Inc',
            location='New York, NY',
            job_type='full-time',
            category='customer-care',
            description='Help customers with their needs',
            requirements='Excellent communication skills',
            salary_range='$35,000 - $45,000',
            is_remote=False,
            is_featured=False
        )
    
    def test_home_page_loads(self):
        """Test home page loads correctly"""
        response = self.client.get(reverse('jobs:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'JobRite.com')
        self.assertContains(response, 'Software Developer')
    
    def test_search_functionality(self):
        """Test job search functionality"""
        response = self.client.get(reverse('jobs:search_jobs'), {'q': 'developer'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Software Developer')
        self.assertNotContains(response, 'Customer Service Representative')
    
    def test_contact_page_loads(self):
        """Test contact page loads correctly"""
        response = self.client.get(reverse('jobs:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contact Us')
    
    def test_utility_pages_load(self):
        """Test utility pages load correctly"""
        pages = ['jobs:faq', 'jobs:salary_calculator', 'jobs:cv_creator']
        for page in pages:
            response = self.client.get(reverse(page))
            self.assertEqual(response.status_code, 200)

class JobsFormsTestCase(TestCase):
    """Test cases for jobs app forms"""
    
    def test_job_search_form_validation(self):
        """Test job search form validation"""
        # Valid form
        form_data = {'q': 'developer', 'location': 'Remote'}
        form = JobSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Invalid short query
        form_data = {'q': 'a'}
        form = JobSearchForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_contact_form_validation(self):
        """Test contact form validation"""
        # Valid form
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message with enough characters.'
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Invalid form
        invalid_data = {
            'name': 'A',
            'email': 'invalid-email',
            'subject': 'Test',
            'message': 'Short'
        }
        form = ContactForm(data=invalid_data)
        self.assertFalse(form.is_valid())

class ColorSchemeTestCase(TestCase):
    """Test color scheme implementation"""
    
    def test_color_scheme_in_templates(self):
        """Test that color scheme is properly implemented"""
        response = self.client.get(reverse('jobs:home'))
        self.assertEqual(response.status_code, 200)
        
        # Check for color scheme values
        self.assertContains(response, '#233D4D')  # Primary color
        self.assertContains(response, '#FE7F2D')  # Accent color
        self.assertContains(response, 'Work Sans') # Font family
