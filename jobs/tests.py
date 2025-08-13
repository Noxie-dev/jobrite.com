from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Job, JobApplication, SavedSearch, EmployerProfile
from .forms import JobSearchForm, ContactForm, SavedSearchForm, EmployerProfileForm, JobPostingForm

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
        response = self.client.get(reverse('jobs:search'), {'q': 'developer'})
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


class SavedSearchModelTests(TestCase):
    """Test SavedSearch model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.saved_search = SavedSearch.objects.create(
            user=self.user,
            name='Test Search',
            query='developer',
            location='New York',
            category='it',
            salary_min=50000,
            email_alerts=True
        )

    def test_saved_search_string_representation(self):
        self.assertEqual(str(self.saved_search), "testuser - Test Search")

    def test_saved_search_get_search_url(self):
        url = self.saved_search.get_search_url()
        self.assertIn('/search/?', url)
        self.assertIn('q=developer', url)
        self.assertIn('location=New+York', url)


class EmployerProfileTests(TestCase):
    """Test EmployerProfile model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='employer',
            email='employer@example.com',
            password='testpass123'
        )
        self.employer_profile = EmployerProfile.objects.create(
            user=self.user,
            company_name='Test Company',
            company_description='A test company',
            company_size='11-50',
            contact_email='contact@testcompany.com',
            address_line1='123 Main St',
            city='Test City',
            state_province='Test State',
            postal_code='12345',
            country='United States'
        )

    def test_employer_profile_string_representation(self):
        self.assertEqual(str(self.employer_profile), "Test Company - employer")

    def test_get_full_address(self):
        expected_address = "123 Main St\nTest City, Test State 12345\nUnited States"
        self.assertEqual(self.employer_profile.get_full_address(), expected_address)


class EnhancedJobTests(TestCase):
    """Test enhanced Job model functionality"""
    
    def setUp(self):
        self.job = Job.objects.create(
            title='Test Job',
            company='Test Company',
            location='Test Location',
            job_type='full-time',
            category='it',
            description='Test description',
            requirements='Test requirements',
            salary_range='$50,000 - $70,000',
            salary_min=50000,
            salary_max=70000,
            salary_currency='USD',
            is_active=True
        )

    def test_job_is_recently_posted(self):
        self.assertTrue(self.job.is_recently_posted())
        
        # Create an old job
        old_job = Job.objects.create(
            title='Old Job',
            company='Old Company',
            location='Old Location',
            job_type='full-time',
            category='it',
            description='Old description',
            requirements='Old requirements',
            salary_range='$40,000 - $60,000'
        )
        # Manually set creation time to 10 days ago
        old_job.created_at = timezone.now() - timedelta(days=10)
        old_job.save()
        
        self.assertFalse(old_job.is_recently_posted())

    def test_job_get_salary_display(self):
        # Test with min and max salary
        self.assertEqual(self.job.get_salary_display(), "USD 50,000 - 70,000")
        
        # Test with only min salary
        job_min_only = Job.objects.create(
            title='Test Job 2',
            company='Test Company 2',
            location='Test Location 2',
            job_type='part-time',
            category='sales',
            description='Test description 2',
            requirements='Test requirements 2',
            salary_min=30000,
            salary_currency='USD'
        )
        self.assertEqual(job_min_only.get_salary_display(), "USD 30,000+")
        
        # Test with salary_range fallback
        job_range_only = Job.objects.create(
            title='Test Job 3',
            company='Test Company 3',
            location='Test Location 3',
            job_type='contract',
            category='hr',
            description='Test description 3',
            requirements='Test requirements 3',
            salary_range='Competitive'
        )
        self.assertEqual(job_range_only.get_salary_display(), "Competitive")


class EnhancedSearchTests(TestCase):
    """Test enhanced search functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test jobs with new salary fields
        Job.objects.create(
            title='Python Developer',
            company='Tech Corp',
            location='New York',
            job_type='full-time',
            category='it',
            description='Python development job',
            requirements='Python experience',
            salary_min=70000,
            salary_max=90000,
            is_active=True,
            is_remote=True
        )
        
        Job.objects.create(
            title='Sales Manager',
            company='Sales Inc',
            location='Los Angeles',
            job_type='full-time',
            category='sales',
            description='Sales management position',
            requirements='Sales experience',
            salary_min=60000,
            salary_max=80000,
            is_active=True,
            is_remote=False
        )

    def test_search_with_salary_filters(self):
        """Test search with salary range filters"""
        response = self.client.get(reverse('jobs:search'), {
            'salary_min': '65000'
        })
        self.assertEqual(response.status_code, 200)
        # Should find Python Developer (min 70k) but not Sales Manager (min 60k)
        self.assertContains(response, 'Python Developer')

    def test_search_with_remote_filter(self):
        """Test search with remote work filter"""
        response = self.client.get(reverse('jobs:search'), {
            'is_remote': 'on'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python Developer')
        self.assertNotContains(response, 'Sales Manager')

    def test_search_with_date_posted_filter(self):
        """Test search with date posted filter"""
        response = self.client.get(reverse('jobs:search'), {
            'date_posted': '7'  # Past week
        })
        self.assertEqual(response.status_code, 200)
        # Both jobs should appear as they were just created
        self.assertContains(response, 'Python Developer')
        self.assertContains(response, 'Sales Manager')


class SavedSearchViewTests(TestCase):
    """Test saved search functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_saved_searches_view_requires_login(self):
        response = self.client.get(reverse('jobs:saved_searches'))
        self.assertRedirects(response, '/users/login/?next=/saved-searches/')

    def test_saved_searches_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('jobs:saved_searches'))
        self.assertEqual(response.status_code, 200)

    def test_save_search_requires_login(self):
        response = self.client.post(reverse('jobs:save_search'))
        self.assertRedirects(response, '/users/login/?next=/save-search/')
