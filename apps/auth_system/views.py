from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta
import random
import logging
from .forms import CustomUserCreationForm

logger = logging.getLogger(__name__)


def login_selection(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'auth/login_selection.html')


def team_login(request):
    """Staff/admin portal — customers are blocked."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            user_role = getattr(getattr(user, 'role', None), 'role', None)
            allowed = {'superadmin', 'admin', 'subadmin', 'staff', 'supervisor'}
            if user.is_staff or user.is_superuser or user_role in allowed:
                login(request, user)
                request.session['login_verified'] = True
                return redirect('dashboard')
            else:
                messages.error(request, 'This portal is for staff only. Please use Customer Login.')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'auth/team_login.html')


def customer_login(request):
    """Customer portal."""
    if request.user.is_authenticated:
        return redirect('customer_dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['login_verified'] = True
            user_role = getattr(getattr(user, 'role', None), 'role', None)
            if user.is_staff or user.is_superuser or user_role in {'superadmin', 'admin', 'subadmin', 'staff', 'supervisor'}:
                return redirect('dashboard')
            return redirect('customer_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'auth/customer_login.html')


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            account_type = form.cleaned_data.get('account_type', 'customer')
            _send_welcome_email(user, account_type)
            if account_type == 'staff_request':
                messages.info(request, 'Staff request submitted! You can use the platform as a customer meanwhile.')
            else:
                messages.success(request, 'Account created! You can now log in.')
            return redirect('auth:customer_login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/register.html', {'form': form})


def logout_view(request):
    logout(request)
    request.session.flush()
    messages.success(request, 'Logged out successfully.')
    return redirect('auth:login_selection')


def forgot_password(request):
    return render(request, 'auth/forgot_password.html')


@require_http_methods(["POST"])
def send_reset_code(request):
    email = request.POST.get('email', '').strip()
    if not email:
        return JsonResponse({'success': False, 'message': 'Email is required'})
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({'success': True, 'message': 'If that email exists, a code has been sent.'})

    code = str(random.randint(100000, 999999))
    request.session['reset_code'] = code
    request.session['reset_email'] = email
    request.session['reset_code_time'] = timezone.now().isoformat()
    request.session['reset_attempts'] = 0

    try:
        send_mail(
            'MultiStock — Password Reset Code',
            f'Hi {user.username},\n\nYour reset code: {code}\n\nExpires in 10 minutes. Do not share it.\n\n— MultiStock',
            settings.DEFAULT_FROM_EMAIL, [email]
        )
    except Exception as e:
        logger.error(f"Reset email failed: {e}")
    return JsonResponse({'success': True, 'message': 'If that email exists, a code has been sent.'})


@require_http_methods(["POST"])
def verify_reset_code(request):
    code = request.POST.get('code', '').strip()
    session_code = request.session.get('reset_code')
    code_time_str = request.session.get('reset_code_time')
    attempts = request.session.get('reset_attempts', 0)
    max_attempts = getattr(settings, 'OTP_MAX_ATTEMPTS', 3)

    if not session_code or not code_time_str:
        return JsonResponse({'success': False, 'message': 'No reset request found. Please start over.'})
    if attempts >= max_attempts:
        for k in ['reset_code', 'reset_code_time', 'reset_attempts']:
            request.session.pop(k, None)
        return JsonResponse({'success': False, 'message': 'Too many attempts. Request a new code.'})

    expiry = getattr(settings, 'OTP_EXPIRY_SECONDS', 600)
    code_time = datetime.fromisoformat(code_time_str)
    if timezone.now() > code_time + timedelta(seconds=expiry):
        request.session.pop('reset_code', None)
        return JsonResponse({'success': False, 'message': 'Code expired. Request a new one.'})

    if code != session_code:
        request.session['reset_attempts'] = attempts + 1
        remaining = max_attempts - attempts - 1
        return JsonResponse({'success': False, 'message': f'Invalid code. {remaining} attempt(s) left.'})

    request.session['reset_verified'] = True
    return JsonResponse({'success': True})


@require_http_methods(["POST"])
def reset_password(request):
    if not request.session.get('reset_verified'):
        return JsonResponse({'success': False, 'message': 'Please verify your code first.'})
    email = request.session.get('reset_email')
    new_password = request.POST.get('new_password', '')
    confirm = request.POST.get('confirm_password', '')
    if len(new_password) < 8:
        return JsonResponse({'success': False, 'message': 'Password must be at least 8 characters.'})
    if new_password != confirm:
        return JsonResponse({'success': False, 'message': 'Passwords do not match.'})
    try:
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        for k in ['reset_code', 'reset_email', 'reset_code_time', 'reset_attempts', 'reset_verified']:
            request.session.pop(k, None)
        return JsonResponse({'success': True, 'message': 'Password reset! You can now log in.'})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'})


def guest_access(request):
    from django.http import HttpResponseRedirect
    return HttpResponseRedirect('/guest/dashboard/')


def api_team_users(request):
    from django.contrib.auth.models import User
    users = list(User.objects.filter(is_staff=True).values('id', 'username', 'email'))
    return JsonResponse({'users': users})


def demo_google_callback(request):
    messages.info(request, 'Google login is not available in demo mode.')
    return redirect('auth:login_selection')


def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})


def change_password_api(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST required'})
    from django.contrib.auth import update_session_auth_hash
    old = request.POST.get('old_password', '')
    new = request.POST.get('new_password', '')
    if not request.user.check_password(old):
        return JsonResponse({'success': False, 'message': 'Current password is incorrect'})
    if len(new) < 8:
        return JsonResponse({'success': False, 'message': 'Password must be at least 8 characters'})
    request.user.set_password(new)
    request.user.save()
    update_session_auth_hash(request, request.user)
    return JsonResponse({'success': True, 'message': 'Password changed successfully'})


def _send_welcome_email(user, account_type):
    try:
        send_mail(
            'Welcome to MultiStock Platform!',
            f'Hi {user.username},\n\nWelcome to MultiStock!\n\nGet started: https://multi-stock-logistics-platform-7jyj.onrender.com\n\n— The MultiStock Team',
            settings.DEFAULT_FROM_EMAIL, [user.email]
        )
    except Exception as e:
        logger.error(f"Welcome email failed for {user.username}: {e}")
