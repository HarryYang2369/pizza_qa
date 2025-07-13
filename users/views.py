from django.contrib.auth import login, authenticate, logout
from .forms import StudentRegistrationForm, TeacherRegistrationForm, LoginForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import CustomUser

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

# def register_teacher(request):
#     if request.method == 'POST':
#         form = TeacherRegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             messages.success(request, "Registration successful!")
#             return redirect('qa:year_selection')
#     else:
#         form = TeacherRegistrationForm()
    
#     context = {
#         'form': form,
#         'user_type': 'teacher'
#     }
#     return render(request, 'users/register.html', context)

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
    """Log the user out and redirect to the home page."""
    logout(request)
    # Change this redirect to use the namespaced URL
    return redirect('users:login')

# Add this test function to check if user is a teacher
def teacher_check(user):
    return user.role == 'teacher'

@login_required
@user_passes_test(teacher_check, login_url='login')
def student_management(request):
    students = CustomUser.objects.filter(role='student').order_by('id')
    context = {'students': students}
    return render(request, 'users/student_management.html', context)

@login_required
@user_passes_test(teacher_check, login_url='login')
def delete_student(request, student_id):
    """View to delete a student account"""
    student = get_object_or_404(CustomUser, id=student_id, role='student')
    
    if request.method == 'POST':
        # Double-check that user is a teacher before deleting
        if request.user.role == 'teacher':
            student.delete()
            messages.success(request, f"Student account for {student.real_name} has been deleted.")
            return redirect('users:student_management')
        else:
            messages.error(request, "You don't have permission to perform this action.")
            return redirect('login')
    
    context = {'student': student}
    return render(request, 'users/confirm_delete.html', context)