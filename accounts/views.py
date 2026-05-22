from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_approved = False  # Ensure it's false for new registrations
            user.save()
            messages.success(request, "Registration request submitted! Please wait for an Admin to approve your account.")
            return redirect('login')
        else:
            messages.error(request, "Registration failed. Please correct the errors.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_approved and not user.is_admin():
                messages.warning(request, "Your account is pending approval by an Admin.")
                return redirect('login')
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

@login_required
def approve_users_view(request):
    if not request.user.is_admin():
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    pending_users = User.objects.filter(is_approved=False).exclude(role='ADMIN')
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        target_user = User.objects.get(id=user_id)
        
        if action == 'approve':
            target_user.is_approved = True
            target_user.save()
            messages.success(request, f"User {target_user.username} approved!")
        elif action == 'reject':
            target_user.delete()
            messages.warning(request, f"User {target_user.username} registration rejected.")
        return redirect('approve_users')
        
    return render(request, 'accounts/approve_users.html', {'pending_users': pending_users})
