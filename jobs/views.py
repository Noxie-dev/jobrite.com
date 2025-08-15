from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from .models import Job, JobApplication, SavedSearch, EmployerProfile
from .forms import JobSearchForm, ContactForm, JobApplicationForm, SavedSearchForm, EmployerProfileForm, JobPostingForm

def home(request):
    """Home page view with job categories and featured jobs"""
    
    try:
        # Get job categories with counts
        job_categories = []
        category_choices = Job.CATEGORY_CHOICES
        
        for category_key, category_name in category_choices:
            try:
                job_count = Job.objects.filter(category=category_key).count()
            except Exception:
                job_count = 0
            job_categories.append({
                'key': category_key,
                'name': category_name,
                'count': job_count,
                'description': get_category_description(category_key)
            })
        
        # Get featured jobs (limit to 6 for home page)
        try:
            featured_jobs = Job.objects.filter(is_featured=True)[:6]
        except Exception:
            featured_jobs = []
        
        # Get remote jobs specifically for the remote section
        try:
            remote_jobs = Job.objects.filter(is_remote=True, category__in=['it', 'logistics'])[:2]
        except Exception:
            remote_jobs = []
        
        # Get recent jobs
        try:
            recent_jobs = Job.objects.all()[:8]
        except Exception:
            recent_jobs = []
        
        # Get total jobs count
        try:
            total_jobs = Job.objects.count()
        except Exception:
            total_jobs = 0
            
    except Exception as e:
        # If all database queries fail, provide default data
        job_categories = [
            {'key': 'it', 'name': 'IT & Technology', 'count': 0, 'description': 'Technology roles'},
            {'key': 'sales', 'name': 'Sales', 'count': 0, 'description': 'Sales opportunities'},
            {'key': 'hr', 'name': 'Human Resources', 'count': 0, 'description': 'HR positions'},
        ]
        featured_jobs = []
        remote_jobs = []
        recent_jobs = []
        total_jobs = 0
    
    context = {
        'page_title': 'Find Your Perfect Job',
        'job_categories': job_categories,
        'featured_jobs': featured_jobs,
        'remote_jobs': remote_jobs,
        'recent_jobs': recent_jobs,
        'total_jobs': total_jobs,
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
    """Enhanced job search functionality with advanced filters"""
    form = JobSearchForm(request.GET or None)
    jobs = Job.objects.filter(is_active=True)  # Only show active jobs
    
    if form.is_valid():
        # Get cleaned data from form
        query = form.cleaned_data.get('q', '').strip()
        location = form.cleaned_data.get('location', '').strip()
        category = form.cleaned_data.get('category', '')
        job_type = form.cleaned_data.get('job_type', '')
        salary_min = form.cleaned_data.get('salary_min')
        salary_max = form.cleaned_data.get('salary_max')
        is_remote = form.cleaned_data.get('is_remote')
        date_posted = form.cleaned_data.get('date_posted')
        
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
        
        # Advanced filters
        if salary_min:
            jobs = jobs.filter(
                Q(salary_min__gte=salary_min) | Q(salary_min__isnull=True)
            )
        
        if salary_max:
            jobs = jobs.filter(
                Q(salary_max__lte=salary_max) | Q(salary_max__isnull=True)
            )
        
        if is_remote:
            jobs = jobs.filter(is_remote=True)
        
        # Filter by date posted
        if date_posted:
            days = int(date_posted)
            date_threshold = timezone.now() - timedelta(days=days)
            jobs = jobs.filter(created_at__gte=date_threshold)
        
        # Order by relevance (featured first, then by creation date)
        jobs = jobs.order_by('-is_featured', '-created_at')
        
        # Show success message if search was performed
        search_performed = any([query, location, category, job_type, salary_min, salary_max, is_remote, date_posted])
        if search_performed:
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
    
    # Get user's saved searches if authenticated
    saved_searches = []
    if request.user.is_authenticated:
        saved_searches = SavedSearch.objects.filter(user=request.user)[:5]  # Show recent 5
    
    context = {
        'page_title': 'Job Search',
        'form': form,
        'jobs': jobs,
        'total_results': total_results,
        'has_search': bool(request.GET),
        'categories': categories,
        'job_types': job_types,
        'saved_searches': saved_searches,
        # Current search values for form persistence
        'query': form.cleaned_data.get('q', '') if form.is_valid() else request.GET.get('q', ''),
        'location': form.cleaned_data.get('location', '') if form.is_valid() else request.GET.get('location', ''),
        'selected_category': form.cleaned_data.get('category', '') if form.is_valid() else request.GET.get('category', ''),
        'selected_job_type': form.cleaned_data.get('job_type', '') if form.is_valid() else request.GET.get('job_type', ''),
        'salary_min': form.cleaned_data.get('salary_min') if form.is_valid() else request.GET.get('salary_min', ''),
        'salary_max': form.cleaned_data.get('salary_max') if form.is_valid() else request.GET.get('salary_max', ''),
        'is_remote': form.cleaned_data.get('is_remote') if form.is_valid() else bool(request.GET.get('is_remote')),
        'date_posted': form.cleaned_data.get('date_posted', '') if form.is_valid() else request.GET.get('date_posted', ''),
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


def job_detail(request, job_id):
    """Job detail view with application functionality"""
    job = get_object_or_404(Job, id=job_id)
    
    # Check if user has already applied
    has_applied = False
    user_application = None
    if request.user.is_authenticated:
        try:
            user_application = JobApplication.objects.get(job=job, applicant=request.user)
            has_applied = True
        except JobApplication.DoesNotExist:
            pass
    
    context = {
        'page_title': f'{job.title} at {job.company}',
        'job': job,
        'has_applied': has_applied,
        'user_application': user_application,
    }
    return render(request, 'jobs/job_detail.html', context)


@login_required
def apply_for_job(request, job_id):
    """Apply for a job"""
    job = get_object_or_404(Job, id=job_id)
    
    # Check if user has already applied
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('jobs:job_detail', job_id=job.id)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            
            messages.success(request, f'Your application for {job.title} has been submitted successfully!')
            return redirect('jobs:job_detail', job_id=job.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = JobApplicationForm()
    
    context = {
        'page_title': f'Apply for {job.title}',
        'job': job,
        'form': form,
    }
    return render(request, 'jobs/apply_job.html', context)


@login_required
@require_POST
def quick_apply(request, job_id):
    """Quick apply for a job via AJAX"""
    job = get_object_or_404(Job, id=job_id)
    
    # Check if user has already applied
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        return JsonResponse({
            'success': False,
            'message': 'You have already applied for this job.'
        })
    
    # Create application without cover letter or resume
    application = JobApplication.objects.create(
        job=job,
        applicant=request.user
    )
    
    return JsonResponse({
        'success': True,
        'message': f'Your application for {job.title} has been submitted successfully!'
    })


@login_required
def my_applications(request):
    """View user's job applications"""
    applications = JobApplication.objects.filter(applicant=request.user).select_related('job')
    
    context = {
        'page_title': 'My Applications',
        'applications': applications,
    }
    return render(request, 'jobs/my_applications.html', context)


@login_required
def withdraw_application(request, application_id):
    """Withdraw a job application"""
    application = get_object_or_404(JobApplication, id=application_id, applicant=request.user)
    
    if application.status in ['accepted', 'rejected']:
        messages.error(request, 'Cannot withdraw an application that has already been processed.')
        return redirect('jobs:my_applications')
    
    if request.method == 'POST':
        application.status = 'withdrawn'
        application.save()
        messages.success(request, f'Your application for {application.job.title} has been withdrawn.')
        return redirect('jobs:my_applications')
    
    context = {
        'page_title': 'Withdraw Application',
        'application': application,
    }
    return render(request, 'jobs/withdraw_application.html', context)


@login_required
def save_search(request):
    """Save current search criteria"""
    if request.method == 'POST':
        form = SavedSearchForm(request.POST, user=request.user)
        if form.is_valid():
            saved_search = form.save(commit=False)
            saved_search.user = request.user
            
            # Get search parameters from POST data
            saved_search.query = request.POST.get('search_query', '')
            saved_search.location = request.POST.get('search_location', '')
            saved_search.category = request.POST.get('search_category', '')
            saved_search.job_type = request.POST.get('search_job_type', '')
            
            # Advanced filters
            salary_min = request.POST.get('search_salary_min')
            salary_max = request.POST.get('search_salary_max')
            if salary_min:
                try:
                    saved_search.salary_min = float(salary_min)
                except ValueError:
                    pass
            if salary_max:
                try:
                    saved_search.salary_max = float(salary_max)
                except ValueError:
                    pass
            
            saved_search.is_remote = bool(request.POST.get('search_is_remote'))
            saved_search.date_posted = request.POST.get('search_date_posted', '')
            
            saved_search.save()
            messages.success(request, f'Search "{saved_search.name}" has been saved successfully!')
            return JsonResponse({'success': True, 'message': 'Search saved successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@login_required
def saved_searches(request):
    """View user's saved searches"""
    searches = SavedSearch.objects.filter(user=request.user)
    
    context = {
        'page_title': 'My Saved Searches',
        'searches': searches,
    }
    return render(request, 'jobs/saved_searches.html', context)


@login_required
def delete_saved_search(request, search_id):
    """Delete a saved search"""
    search = get_object_or_404(SavedSearch, id=search_id, user=request.user)
    
    if request.method == 'POST':
        search_name = search.name
        search.delete()
        messages.success(request, f'Saved search "{search_name}" has been deleted.')
        return redirect('jobs:saved_searches')
    
    context = {
        'page_title': 'Delete Saved Search',
        'search': search,
    }
    return render(request, 'jobs/delete_saved_search.html', context)


# Employer views
@login_required
def employer_dashboard(request):
    """Dashboard for employers to manage their jobs"""
    try:
        employer_profile = request.user.employer_profile
    except EmployerProfile.DoesNotExist:
        messages.info(request, 'Please complete your employer profile to start posting jobs.')
        return redirect('jobs:employer_profile')
    
    # Get employer's jobs
    jobs = Job.objects.filter(company=employer_profile.company_name).order_by('-created_at')
    
    context = {
        'page_title': 'Employer Dashboard',
        'employer_profile': employer_profile,
        'jobs': jobs,
        'total_jobs': jobs.count(),
        'active_jobs': jobs.filter(is_active=True).count(),
    }
    return render(request, 'jobs/employer_dashboard.html', context)


@login_required
def employer_profile(request):
    """Create or edit employer profile"""
    try:
        profile = request.user.employer_profile
    except EmployerProfile.DoesNotExist:
        profile = None
    
    if request.method == 'POST':
        form = EmployerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            
            messages.success(request, 'Your employer profile has been updated successfully!')
            return redirect('jobs:employer_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmployerProfileForm(instance=profile)
    
    context = {
        'page_title': 'Employer Profile' if profile else 'Create Employer Profile',
        'form': form,
        'profile': profile,
    }
    return render(request, 'jobs/employer_profile.html', context)


@login_required
def post_job(request):
    """Post a new job"""
    try:
        employer_profile = request.user.employer_profile
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Please complete your employer profile before posting jobs.')
        return redirect('jobs:employer_profile')
    
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            # Auto-fill company name from employer profile
            job.company = employer_profile.company_name
            job.save()
            
            messages.success(request, f'Job "{job.title}" has been posted successfully!')
            return redirect('jobs:employer_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill form with employer's company name
        initial_data = {'company': employer_profile.company_name}
        form = JobPostingForm(initial=initial_data)
    
    context = {
        'page_title': 'Post a Job',
        'form': form,
        'employer_profile': employer_profile,
    }
    return render(request, 'jobs/post_job.html', context)


@login_required
def edit_job(request, job_id):
    """Edit an existing job posting"""
    try:
        employer_profile = request.user.employer_profile
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Access denied.')
        return redirect('jobs:home')
    
    job = get_object_or_404(Job, id=job_id, company=employer_profile.company_name)
    
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job)
        if form.is_valid():
            job = form.save()
            messages.success(request, f'Job "{job.title}" has been updated successfully!')
            return redirect('jobs:employer_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = JobPostingForm(instance=job)
    
    context = {
        'page_title': f'Edit Job: {job.title}',
        'form': form,
        'job': job,
        'employer_profile': employer_profile,
    }
    return render(request, 'jobs/edit_job.html', context)


@login_required
def job_applications_view(request, job_id):
    """View applications for a specific job"""
    try:
        employer_profile = request.user.employer_profile
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Access denied.')
        return redirect('jobs:home')
    
    job = get_object_or_404(Job, id=job_id, company=employer_profile.company_name)
    applications = JobApplication.objects.filter(job=job).select_related('applicant').order_by('-applied_at')
    
    context = {
        'page_title': f'Applications for {job.title}',
        'job': job,
        'applications': applications,
        'employer_profile': employer_profile,
    }
    return render(request, 'jobs/job_applications.html', context)
