from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import random
import logging
from .forms import CustomUserCreationForm

logger = logging.getLogger(__name__)

def login_selection(request):
    """Display login selection page"""
    return render(request, 'auth/login_selection.html')

def team_login(request):
    """Team login for internal roles (superadmin/admin/supervisor/staff)"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Allow staff, superusers, and role-mapped team members (subadmin/staff)
            user_role = getattr(getattr(user, 'role', None), 'role', None)
            allowed_roles = {'superadmin', 'admin', 'subadmin', 'staff'}

            logger.info(f"Team login attempt: {username}, is_staff={user.is_staff}, is_superuser={user.is_superuser}, user_role={user_role}")

            if user.is_staff or user.is_superuser or user_role in allowed_roles:
                login(request, user)
                request.session['login_verified'] = True
                logger.info(f"Team login successful for {username}, redirecting to dashboard")
                if messages.get_messages(request):
                    list(messages.get_messages(request))
                return redirect('dashboard')
            else:
                logger.warning(f"Team login denied for {username}: not in allowed roles/staff")
                messages.error(request, 'Access denied. Team credentials required (superadmin/admin/subadmin/staff).')
        else:
            logger.warning(f"Team login failed: invalid credentials for {username}")
            messages.error(request, 'Invalid username or password.')

    return render(request, 'auth/team_login.html')

def customer_login(request):
    """Customer login for marketplace access"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Allow both staff and regular users for customer portal
            login(request, user)
            request.session['login_verified'] = True
            # Clear any previous error messages after successful login
            if messages.get_messages(request):
                list(messages.get_messages(request))  # Clear messages
            # Redirect customers to customer dashboard
            return redirect('customer_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'auth/customer_login.html')

def register_view(request):
    """User registration"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            account_type = form.cleaned_data['account_type']
            
            if account_type == 'staff_request':
                user.is_active = True  # Keep active with customer access
                user.save()
                send_welcome_email(user, 'staff_request')
                messages.info(request, 'Staff access request submitted! Welcome email sent to your inbox. You can use the platform as a customer while waiting for staff approval.')
            else:
                user.is_active = True
                user.save()
                send_welcome_email(user, 'customer')
                messages.success(request, 'Account created successfully! Welcome email sent to your inbox. You can now login.')
            
            return redirect('auth:customer_login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'auth/register.html', {'form': form})

def logout_view(request):
    """Logout user"""
    logout(request)
    request.session.flush()  # Clear entire session including login_verified flag
    messages.success(request, 'You have been logged out successfully.')
    return redirect('auth:login_selection')

def demo_google_callback(request):
    """Demo Google OAuth callback - shows demo message"""
    messages.info(request, 'Google OAuth Demo: This is a demonstration. Configure real Google OAuth credentials for production use.')
    return redirect('auth:login_selection')

def guest_access(request):
    """Allow guest users to browse platform with read-only access"""
    # Use HttpResponseRedirect for explicit redirect
    from django.http import HttpResponseRedirect
    return HttpResponseRedirect('/guest/dashboard/')

def forgot_password(request):
    """Forgot password page"""
    return render(request, 'auth/forgot_password.html')

@require_http_methods(["POST"])
def send_reset_code(request):
    """Send password reset verification code via email"""
    try:
        email = request.POST.get('email')
        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required'})
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'No account found with this email'})
        
        # Generate 6-digit code
        code = str(random.randint(100000, 999999))
        
        # Store code in session
        request.session['reset_code'] = code
        request.session['reset_email'] = email
        request.session['reset_code_time'] = str(timezone.now())
        
        # Send email
        subject = 'MultiStock - Password Reset Code'
        message = f'''Hi {user.username},

You requested to reset your password for your MultiStock account.

Your verification code is: {code}

This code will expire in 15 minutes.

If you didn't request this, please ignore this email.

Best regards,
MultiStock Team'''
        
        logger.info(f"Sending password reset code to {email}")
        print(f"\n=== PASSWORD RESET CODE ===")
        print(f"To: {email}")
        print(f"Code: {code}")
        print(f"========================\n")
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        logger.info(f"✅ Password reset code sent to {email}")
        return JsonResponse({'success': True, 'message': 'Verification code sent to your email'})
        
    except Exception as e:
        logger.error(f"❌ Failed to send reset code: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

@require_http_methods(["POST"])
def verify_reset_code(request):
    """Verify the reset code and allow password change"""
    try:
        code = request.POST.get('code')
        new_password = request.POST.get('new_password')
        
        if not code or not new_password:
            return JsonResponse({'success': False, 'message': 'Code and new password are required'})
        
        # Check session
        stored_code = request.session.get('reset_code')
        stored_email = request.session.get('reset_email')
        
        if not stored_code or not stored_email:
            return JsonResponse({'success': False, 'message': 'No reset request found. Please request a new code'})
        
        # Verify code
        if code != stored_code:
            return JsonResponse({'success': False, 'message': 'Invalid verification code'})
        
        # Update password
        user = User.objects.get(email=stored_email)
        user.set_password(new_password)
        user.save()
        
        # Clear session
        del request.session['reset_code']
        del request.session['reset_email']
        if 'reset_code_time' in request.session:
            del request.session['reset_code_time']
        
        logger.info(f"✅ Password reset successful for {stored_email}")
        return JsonResponse({'success': True, 'message': 'Password reset successful! You can now login'})
        
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'})
    except Exception as e:
        logger.error(f"❌ Failed to verify reset code: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

def profile_view(request):
    """User profile page"""
    if request.method == 'POST':
        try:
            user = request.user
            user.email = request.POST.get('email', user.email)
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.save()
            messages.success(request, 'Profile updated successfully!')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
        return redirect('profile')
    
    from orders.models import OrderListModel
    try:
        total_orders = OrderListModel.objects.filter(openid=request.user.openid).count()
    except:
        total_orders = 0
    
    context = {
        'user': request.user,
        'total_orders': total_orders,
    }
    return render(request, 'profile.html', context)

def send_welcome_email(user, account_type):
    """Send welcome email to new users"""
    try:
        if account_type == 'staff_request':
            subject = 'Welcome to MultiStock - Staff Access Request Received'
            message = f'''
Hi {user.username},

Welcome to MultiStock! Your account has been created successfully.

Your staff access request has been submitted and is pending approval from our team. In the meantime, you can explore our platform with customer-level access.

Account Details:
- Username: {user.username}
- Email: {user.email}
- Account Type: Staff Access Request
- Status: Customer access while pending approval

You can login at: http://127.0.0.1:8000/auth/customer-login/

Thank you for joining MultiStock!

Best regards,
MultiStock Team
            '''
        else:
            subject = 'Welcome to MultiStock - Account Created Successfully'
            message = f'''
Hi {user.username},

Welcome to MultiStock! Your account has been created successfully.

Account Details:
- Username: {user.username}
- Email: {user.email}
- Account Type: Customer
- Status: Active

You can now login and start exploring our marketplace:
- Browse products and services
- Place orders and track shipments
- Participate in auctions
- Join community forums

Login at: http://127.0.0.1:8000/auth/customer-login/

Thank you for joining MultiStock!

Best regards,
MultiStock Team
            '''
        
        print(f"\n=== SENDING WELCOME EMAIL ===")
        print(f"To: {user.email}")
        print(f"Subject: {subject}")
        print(f"Message: {message}")
        print(f"=== EMAIL SENT ===")
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"\n❌ FAILED to send welcome email to {user.email}: {str(e)}")
        print(f"Error details: {type(e).__name__}")


@require_http_methods(["POST"])
def change_password_api(request):
    """API endpoint to change user password"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'You must be logged in'}, status=401)
    
    try:
        import json
        data = json.loads(request.body)
        current_password = data.get('current_password', '').strip()
        new_password = data.get('new_password', '').strip()
        
        if not current_password or not new_password:
            return JsonResponse({'success': False, 'message': 'Please provide all required fields'})
        
        user = request.user
        
        # Verify current password
        if not user.check_password(current_password):
            return JsonResponse({'success': False, 'message': 'Current password is incorrect'})
        
        # Validate new password
        if len(new_password) < 8:
            return JsonResponse({'success': False, 'message': 'New password must be at least 8 characters long'})
        
        if current_password == new_password:
            return JsonResponse({'success': False, 'message': 'New password must be different from current password'})
        
        # Change password
        user.set_password(new_password)
        user.save()
        
        return JsonResponse({'success': True, 'message': 'Password changed successfully'})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid request data'})
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        return JsonResponse({'success': False, 'message': 'An error occurred while changing password'})


@require_http_methods(["GET"])
def api_team_users(request):
    """API endpoint to fetch team users from database for login page demo"""
    try:
        from django.db.models import Q
        
        # Get all staff users with their roles
        team_users = User.objects.filter(
            Q(is_staff=True) | Q(is_superuser=True)
        ).select_related('role').order_by('role__role', 'username')
        
        # Group by role
        users_by_role = {}
        for user in team_users:
            try:
                role = user.role.role if hasattr(user, 'role') else 'staff'
            except:
                role = 'staff'
            
            if role not in users_by_role:
                users_by_role[role] = []
            
            users_by_role[role].append({
                'username': user.username,
                'email': user.email,
                'role': role
            })
        
        return JsonResponse({
            'success': True,
            'users_by_role': users_by_role
        })
    except Exception as e:
        logger.error(f"Error fetching team users: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)