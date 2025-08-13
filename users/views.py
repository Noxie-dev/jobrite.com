from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.conf import settings
from .models import UserProfile, EmailVerification
from .forms import UserProfileForm, UserRegistrationForm, OnboardingForm, CustomPasswordResetForm, CustomSetPasswordForm

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
    """User registration view with email verification"""
    if request.user.is_authenticated:
        return redirect('jobs:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User inactive until email verified
            user.save()
            
            # Create email verification
            email_verification = EmailVerification.objects.create(user=user)
            
            # Send verification email
            if email_verification.send_verification_email():
                messages.success(
                    request, 
                    f'Account created successfully! Please check your email ({user.email}) to verify your account.'
                )
                return redirect('users:email_verification_sent')
            else:
                messages.error(request, 'Account created but failed to send verification email. Please contact support.')
                return redirect('users:login')
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
    """User login view with email verification check"""
    if request.user.is_authenticated:
        return redirect('jobs:home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Check if email is verified
                try:
                    email_verification = user.email_verification
                    if not email_verification.is_verified:
                        messages.error(
                            request, 
                            'Please verify your email address before logging in. Check your inbox for the verification link.'
                        )
                        return render(request, 'registration/login.html', {'form': form, 'page_title': 'Sign In'})
                except EmailVerification.DoesNotExist:
                    # For existing users without email verification records
                    pass
                
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


class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view with custom form and template"""
    form_class = CustomPasswordResetForm
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('users:password_reset_done')
    
    def form_valid(self, form):
        """Add success message when form is valid"""
        messages.success(
            self.request, 
            'Password reset email has been sent! Please check your inbox and follow the instructions.'
        )
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Reset Your Password'
        return context


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Custom password reset confirm view with custom form and template"""
    form_class = CustomSetPasswordForm
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')
    
    def form_valid(self, form):
        """Add success message when password is reset"""
        messages.success(
            self.request,
            'Your password has been reset successfully! You can now log in with your new password.'
        )
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Set New Password'
        return context


def password_reset_done(request):
    """Password reset done view"""
    context = {
        'page_title': 'Password Reset Sent',
    }
    return render(request, 'registration/password_reset_done.html', context)


def password_reset_complete(request):
    """Password reset complete view"""
    context = {
        'page_title': 'Password Reset Complete',
    }
    return render(request, 'registration/password_reset_complete.html', context)


# Email verification views
def email_verification_sent(request):
    """Show email verification sent page"""
    context = {
        'page_title': 'Email Verification Sent',
    }
    return render(request, 'registration/email_verification_sent.html', context)


def verify_email(request, token):
    """Verify email address using token"""
    try:
        email_verification = EmailVerification.objects.get(token=token)
        
        if email_verification.is_verified:
            messages.info(request, 'Your email has already been verified. You can now log in.')
            return redirect('users:login')
        
        if email_verification.is_expired():
            messages.error(
                request, 
                'This verification link has expired. Please request a new verification email.'
            )
            return redirect('users:resend_verification', user_id=email_verification.user.id)
        
        # Verify the email
        if email_verification.verify_email():
            # Activate the user account
            user = email_verification.user
            user.is_active = True
            user.save()
            
            # Log the user in automatically
            login(request, user)
            messages.success(
                request, 
                f'Welcome to JobRite, {user.first_name}! Your email has been verified. Let\'s set up your profile.'
            )
            return redirect('users:onboarding')
        else:
            messages.error(request, 'Verification link has expired. Please request a new one.')
            return redirect('users:resend_verification', user_id=email_verification.user.id)
            
    except EmailVerification.DoesNotExist:
        messages.error(request, 'Invalid verification link. Please check the link or request a new one.')
        return redirect('users:login')


def resend_verification(request, user_id=None):
    """Resend email verification"""
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                user = User.objects.get(email=email, is_active=False)
                email_verification, created = EmailVerification.objects.get_or_create(user=user)
                
                # Reset verification if it exists
                if not created:
                    email_verification.is_verified = False
                    email_verification.save()
                
                if email_verification.send_verification_email():
                    messages.success(
                        request, 
                        f'Verification email sent to {email}. Please check your inbox.'
                    )
                else:
                    messages.error(request, 'Failed to send verification email. Please try again later.')
                    
            except User.DoesNotExist:
                # Don't reveal if email exists for security
                messages.success(
                    request, 
                    'If an account with that email exists, a verification email has been sent.'
                )
        return redirect('users:email_verification_sent')
    
    # Pre-fill email if user_id provided
    email = ''
    if user_id:
        try:
            user = User.objects.get(id=user_id, is_active=False)
            email = user.email
        except User.DoesNotExist:
            pass
    
    context = {
        'page_title': 'Resend Email Verification',
        'email': email,
    }
    return render(request, 'registration/resend_verification.html', context)
