from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone
from .models import Project, CommunityChallenge, CustomUser
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .models import CustomUser, Project, CommunityChallenge



def user_logout(request):
    logout(request)
    return redirect('login')  

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = CustomUser  # Use your custom user model
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def dashboard(request):
    # Add dashboard-specific context
    return render(request, 'dashboard.html')

@login_required
def project_list(request):
    """List all projects with pagination"""
    projects = Project.objects.all().select_related('creator').prefetch_related('skills_needed')
    return render(request, 'projects/list.html', {'projects': projects})

@login_required
def project_detail(request, pk):
    """Project detail view with participation check"""
    project = get_object_or_404(
        Project.objects.select_related('creator')
                      .prefetch_related('participants', 'skills_needed'), 
        pk=pk
    )
    is_participant = request.user in project.participants.all()
    return render(request, 'projects/detail.html', {
        'project': project,
        'is_participant': is_participant
    })

@login_required
def current_challenges(request):
    """List current challenges with participation status"""
    challenges = CommunityChallenge.objects.filter(
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).prefetch_related('participants')
    
    # Annotate with user participation status
    for challenge in challenges:
        challenge.user_is_participant = request.user in challenge.participants.all()
    
    return render(request, 'challenges/current.html', {'challenges': challenges})
