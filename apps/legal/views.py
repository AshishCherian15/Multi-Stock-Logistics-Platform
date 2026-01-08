from django.shortcuts import render

def terms(request):
    return render(request, 'legal/terms.html')

def privacy(request):
    return render(request, 'legal/privacy.html')

def cookies(request):
    return render(request, 'legal/cookies.html')

def license(request):
    return render(request, 'legal/license.html')
