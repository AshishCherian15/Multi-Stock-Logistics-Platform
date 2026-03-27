"""
Exit guest mode and return to login selection
"""
from django.shortcuts import redirect


def exit_guest_mode(request):
    """Exit guest mode and return to login selection"""
    # Clear guest mode session
    if 'guest_mode' in request.session:
        del request.session['guest_mode']
    
    # Redirect to home (login selection)
    return redirect('/')
