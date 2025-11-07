from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model, login
from django.db.models import Sum, Count
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from vault.models import EncryptedFile, FileAccessLog

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'

@login_required
def dashboard(request):
    # Get user's file statistics
    total_files = EncryptedFile.objects.filter(user=request.user).count()
    total_size = EncryptedFile.objects.filter(user=request.user).aggregate(Sum('file_size'))['file_size__sum'] or 0
    recent_activities = FileAccessLog.objects.filter(
        file__user=request.user
    ).select_related('file').order_by('-timestamp')[:5]
    recent_activity_count = FileAccessLog.objects.filter(file__user=request.user).count()

    context = {
        'total_files': total_files,
        'total_size': total_size,
        'recent_activities': recent_activities,
        'recent_activity_count': recent_activity_count,
    }
    return render(request, 'users/dashboard.html', context)

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/signup.html', {'form': form})

@login_required
def profile(request):
    try:
        if request.method == 'POST':
            form = UserProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('profile')
        else:
            form = UserProfileForm(instance=request.user)
        
        return render(request, 'users/profile.html', {
            'form': form,
            'user': request.user
        })
    except Exception as e:
        print(f"Profile error: {str(e)}")  # For debugging
        messages.error(request, 'An error occurred while loading your profile.')
        return redirect('dashboard')
