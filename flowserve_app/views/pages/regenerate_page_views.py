from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from flowserve_app.decorators import login_required

@login_required
def regenerate_page(request):
    """Render the regenerate report page"""
    return render(request, 'regenerate.html')
