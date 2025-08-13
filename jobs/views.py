from django.shortcuts import render
from django.db.models import Q
from django.contrib import messages
from .models import Job
from .forms import JobSearchForm, ContactForm

def home(request):
    """Home page view with job categories and featured jobs"""
    
    # Get job categories with counts
    job_categories = []
    category_choices = Job.CATEGORY_CHOICES
    
    for category_key, category_name in category_choices:
        job_count = Job.objects.filter(category=category_key).count()
        job_categories.append({
            'key': category_key,
            'name': category_name,
            'count': job_count,
            'description': get_category_description(category_key)
        })
    
    # Get featured jobs (limit to 6 for home page)
    featured_jobs = Job.objects.filter(is_featured=True)[:6]
    
    # Get remote jobs specifically for the remote section
    remote_jobs = Job.objects.filter(is_remote=True, category__in=['it', 'logistics'])[:2]
    
    # Get recent jobs
    recent_jobs = Job.objects.all()[:8]
    
    context = {
        'page_title': 'Find Your Perfect Job',
        'job_categories': job_categories,
        'featured_jobs': featured_jobs,
        'remote_jobs': remote_jobs,
        'recent_jobs': recent_jobs,
        'total_jobs': Job.objects.count(),
    }
    return render(request, 'home.html', context)

def get_category_description(category_key):
    """Get description for job categories"""
    descriptions = {
        'call-center': 'Customer support roles',
        'customer-care': 'Service excellence roles',
        'sales': 'Revenue generation roles',
        'hr': 'People management roles',
        'it': 'Technology and support roles',
        'logistics': 'Supply chain and coordination',
        'other': 'Various opportunities'
    }
    return descriptions.get(category_key, 'Professional opportunities')

def faq(request):
    """FAQ page view"""
    context = {
        'page_title': 'Frequently Asked Questions',
    }
    return render(request, 'faq.html', context)

def salary_calculator(request):
    """Salary Calculator page view"""
    context = {
        'page_title': 'Salary Calculator',
    }
    return render(request, 'salary_calculator.html', context)

def cv_creator(request):
    """CV Creator page view"""
    context = {
        'page_title': 'CV Creator',
    }
    return render(request, 'cv_creator.html', context)

def search_jobs(request):
    """Job search functionality with form validation"""
    form = JobSearchForm(request.GET or None)
    jobs = Job.objects.all()
    
    if form.is_valid():
        # Get cleaned data from form
        query = form.cleaned_data.get('q', '').strip()
        location = form.cleaned_data.get('location', '').strip()
        category = form.cleaned_data.get('category', '')
        job_type = form.cleaned_data.get('job_type', '')
        
        # Search by query (title, company, description)
        if query:
            jobs = jobs.filter(
                Q(title__icontains=query) |
                Q(company__icontains=query) |
                Q(description__icontains=query) |
                Q(requirements__icontains=query)
            )
        
        # Filter by location
        if location:
            jobs = jobs.filter(location__icontains=location)
        
        # Filter by category
        if category:
            jobs = jobs.filter(category=category)
        
        # Filter by job type
        if job_type:
            jobs = jobs.filter(job_type=job_type)
        
        # Order by relevance (featured first, then by creation date)
        jobs = jobs.order_by('-is_featured', '-created_at')
        
        # Show success message if search was performed
        if any([query, location, category, job_type]):
            messages.success(request, f'Found {jobs.count()} job(s) matching your search criteria.')
    
    else:
        # Handle form errors
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.title()}: {error}')
    
    # Get search statistics
    total_results = jobs.count()
    
    # Get filter options for the search form
    categories = Job.CATEGORY_CHOICES
    job_types = Job.JOB_TYPE_CHOICES
    
    context = {
        'page_title': 'Job Search',
        'form': form,
        'jobs': jobs,
        'total_results': total_results,
        'has_search': bool(request.GET),
        'categories': categories,
        'job_types': job_types,
        'query': form.cleaned_data.get('q', '') if form.is_valid() else request.GET.get('q', ''),
        'location': form.cleaned_data.get('location', '') if form.is_valid() else request.GET.get('location', ''),
        'selected_category': form.cleaned_data.get('category', '') if form.is_valid() else request.GET.get('category', ''),
        'selected_job_type': form.cleaned_data.get('job_type', '') if form.is_valid() else request.GET.get('job_type', ''),
    }
    
    return render(request, 'search_results.html', context)

def contact(request):
    """Contact form view"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process the form (in a real app, you'd send an email or save to database)
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            form = ContactForm()  # Reset form after successful submission
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    
    context = {
        'page_title': 'Contact Us',
        'form': form,
    }
    return render(request, 'contact.html', context)
