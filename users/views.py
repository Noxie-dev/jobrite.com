from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse
from .models import UserProfile
from .forms import UserProfileForm, UserRegistrationForm, OnboardingForm

@login_required
def profile(request, username=None):
    """User profile page view with form handling"""
    if username:
        # View another user's profile
        user = get_object_or_404(User, username=username)
        is_own_profile = user == request.user
    else:
        # View own profile
        user = request.user
        is_own_profile = True
    
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Handle profile update form for own profile
    if is_own_profile and request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=profile) if is_own_profile else None
    
    context = {
        'user': user,
        'profile': profile,
        'form': form,
        'is_own_profile': is_own_profile,
    }
    
    return render(request, 'profile.html', context)

def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('jobs:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in automatically after registration
            login(request, user)
            messages.success(request, f'Welcome to JobRite, {user.first_name}! Let\'s set up your profile.')
            return redirect('users:onboarding')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
        'page_title': 'Create Your Account',
    }
    return render(request, 'registration/register.html', context)

def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('jobs:home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                
                # Check if user has completed onboarding
                profile, created = UserProfile.objects.get_or_create(user=user)
                if not profile.onboarding_completed:
                    return redirect('users:onboarding')
                
                # Redirect to next page or home
                next_page = request.GET.get('next', 'jobs:home')
                return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form,
        'page_title': 'Sign In',
    }
    return render(request, 'registration/login.html', context)

def user_logout(request):
    """User logout view"""
    if request.user.is_authenticated:
        user_name = request.user.first_name or request.user.username
        logout(request)
        messages.success(request, f'You have been logged out successfully. See you soon, {user_name}!')
    return redirect('jobs:home')

@login_required
def onboarding(request):
    """Multi-step onboarding process for new users"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # If onboarding is already completed, redirect to profile
    if profile.onboarding_completed:
        messages.info(request, 'You have already completed the onboarding process.')
        return redirect('users:profile')
    
    step = request.GET.get('step', '1')
    
    if request.method == 'POST':
        form = OnboardingForm(request.POST, request.FILES, instance=profile, step=step)
        if form.is_valid():
            form.save()
            
            # Move to next step or complete onboarding
            if step == '1':
                return redirect(f"{reverse('users:onboarding')}?step=2")
            elif step == '2':
                return redirect(f"{reverse('users:onboarding')}?step=3")
            elif step == '3':
                # Complete onboarding
                profile.onboarding_completed = True
                profile.save()
                messages.success(request, 'Welcome to JobRite! Your profile is now complete.')
                return redirect('jobs:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = OnboardingForm(instance=profile, step=step)
    
    # Calculate progress
    total_steps = 3
    current_step = int(step)
    progress_percentage = (current_step / total_steps) * 100
    
    context = {
        'form': form,
        'step': step,
        'current_step': current_step,
        'total_steps': total_steps,
        'progress_percentage': progress_percentage,
        'page_title': f'Setup Your Profile - Step {step} of {total_steps}',
    }
    return render(request, 'registration/onboarding.html', context)

@login_required
def skip_onboarding(request):
    """Allow users to skip onboarding and complete it later"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    profile.onboarding_completed = True
    profile.save()
    messages.info(request, 'You can complete your profile setup anytime from your profile page.')
    return redirect('jobs:home')
