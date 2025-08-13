from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import BlogPost

class BlogViewsTestCase(TestCase):
    """Test cases for blog app views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.blog_post = BlogPost.objects.create(
            title='Career Tips for Success',
            slug='career-tips-success',
            content='Great tips for career advancement...',
            author=self.user,
            is_published=True
        )
    
    def test_blog_list_page_loads(self):
        """Test blog list page loads correctly"""
        response = self.client.get(reverse('blog:blog_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Career Tips for Success')
    
    def test_blog_search_functionality(self):
        """Test blog search functionality"""
        response = self.client.get(reverse('blog:blog_list'), {'search': 'career'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Career Tips for Success')
        
        # Test search with no results
        response = self.client.get(reverse('blog:blog_list'), {'search': 'nonexistent'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Career Tips for Success')
