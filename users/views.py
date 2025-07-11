from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import StudentRegistrationForm, TeacherRegistrationForm, LoginForm
from django.contrib import messages

def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('qa:year_selection')
    else:
        form = StudentRegistrationForm()
    
    context = {
        'form': form,
        'user_type': 'student'
    }
    return render(request, 'users/register.html', context)

def register_teacher(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('qa:year_selection')
    else:
        form = TeacherRegistrationForm()
    
    context = {
        'form': form,
        'user_type': 'teacher'
    }
    return render(request, 'users/register.html', context)

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('qa:year_selection')
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()
    
    context = {'form': form}
    return render(request, 'users/login.html', context)

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')