from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from .forms import StudentRegistrationForm, TeacherRegistrationForm, LoginForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import CustomUser
from django.contrib.auth.forms import PasswordChangeForm
from qa.models import TeacherSubject, Question, Answer, StudentSubject, Subject

def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('qa:subject_selection')
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
#             return redirect('qa:subject_selection')
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
                return redirect('qa:subject_selection')
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

@login_required
def user_profile(request):
    if request.method == 'POST' and 'change_password' in request.POST:
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password updated successfully!')
            return redirect('users:user_profile')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {'form': form}
    
    if request.user.role == 'teacher':
        # Get subjects taught by teacher
        subjects = TeacherSubject.objects.filter(teacher=request.user)
        
        # Create a list of subject data with student counts
        subject_data = []
        for subject in subjects:
            subject_data.append({
                'obj': subject,
                'student_count': StudentSubject.objects.filter(
                    subject=subject.subject,
                    year=subject.year,
                    teacher=subject.teacher
                ).count()
            })
        
        context['subject_data'] = subject_data
        
    else:
        # Student statistics
        student = request.user
        context.update({
            'total_questions': Question.objects.filter(student=student).count(),
            'resolved_questions': Question.objects.filter(student=student, resolved=True).count(),
            'unresolved_questions': Question.objects.filter(student=student, resolved=False).count(),
            'answers_given': Answer.objects.filter(user=student).count(),
        })
    
    return render(request, 'users/profile.html', context)

@login_required
def manage_students_in_subject(request, subject_id):
    teacher_subject = get_object_or_404(TeacherSubject, id=subject_id, teacher=request.user)
    
    # Get students with their statistics
    students = StudentSubject.objects.filter(
        subject=teacher_subject.subject,
        year=teacher_subject.year,
        teacher=teacher_subject.teacher
    ).select_related('student')
    
    student_data = []
    for student_subject in students:
        student = student_subject.student
        student_data.append({
            'obj': student,
            'questions_asked': Question.objects.filter(
                student=student,
                subject=teacher_subject.subject
            ).count(),
            'answers_given': Answer.objects.filter(user=student).count(),
        })
    
    context = {
        'teacher_subject': teacher_subject,
        'student_data': student_data,
    }
    return render(request, 'users/manage_students_in_subject.html', context)


# users/views.py
@login_required
def manage_questions(request, subject_id, question_type):
    """View for managing questions by subject and type"""
    subject = get_object_or_404(TeacherSubject, id=subject_id, teacher=request.user)
    
    # Permission check for teacher
    if request.user.role != 'teacher':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('users:user_profile')
    
    # Check if teacher teaches this subject
    # if not TeacherSubject.objects.filter(teacher=request.user, subject=subject).exists():
    #     messages.error(request, "You don't teach this subject.")
    #     return redirect('users:teacher_subject_selection', question_type=question_type)
    
    questions = Question.objects.filter(subject=subject.subject).order_by('-created_at')
    
    if question_type == 'general':
        questions = questions.filter(visible_to_teachers=False)
        title = f"General Questions - {subject}"
    else:
        questions = questions.filter(visible_to_teachers=True)
        title = f"Teachers Only Questions - {subject}"
    
    # Filter by resolved status
    resolved = request.GET.get('resolved', None)
    if resolved == 'true':
        questions = questions.filter(resolved=True)
    elif resolved == 'false':
        questions = questions.filter(resolved=False)
    
    context = {
        'subject': subject,
        'questions': questions,
        'question_type': question_type,
        'title': title
    }
    return render(request, 'users/manage_questions.html', context)


# @login_required
# def student_questions(request):
#     subjects = StudentSubject.objects.filter(student=request.user)
#     # Add question count to each subject with a different name
#     for subject in subjects:
#         subject.question_count_value = Question.objects.filter(
#             student=request.user,
#             subject=subject.subject
#         ).count()
    
#     context = {'subjects': subjects}
#     return render(request, 'users/student_questions.html', context)

@login_required
def student_subject_questions(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    questions = Question.objects.filter(
        student=request.user,
        subject=subject
    ).order_by('-created_at')
    
    context = {
        'subject': subject,
        'questions': questions
    }
    return render(request, 'users/student_subject_questions.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('users:user_profile')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'users/change_password.html', {'form': form})

@login_required
def teacher_profile(request):
    teacher = request.user
    subjects = TeacherSubject.objects.filter(teacher=teacher)
    
    # Create a list of subject data with student counts
    subject_data = []
    for subject in subjects:
        subject_data.append({
            'obj': subject,
            'student_count': StudentSubject.objects.filter(
                subject=subject.subject,
                year=subject.year,
                teacher=subject.teacher
            ).count()
        })
    
    context = {
        'teacher': teacher,
        'subject_data': subject_data
    }
    return render(request, 'users/profile_teacher.html', context)

@login_required
def teacher_class_selection(request):
    subjects = TeacherSubject.objects.filter(teacher=request.user)
    context = {'subjects': subjects}
    return render(request, 'users/teacher_class_selection.html', context)

@login_required
def teacher_question_type_selection(request):
    return render(request, 'users/teacher_question_type_selection.html')

@login_required
def teacher_subject_selection(request, question_type):
    subjects = TeacherSubject.objects.filter(teacher=request.user)
    context = {'subjects': subjects, 'question_type': question_type}
    return render(request, 'users/teacher_subject_selection.html', context)

# users/views.py
@login_required
def student_profile(request):
    student = request.user
    context = {
        'student': student,
        'total_questions': Question.objects.filter(student=student).count(),
        'good_questions': Question.objects.filter(student=student, good=True).count(),
        'unresolved_questions': Question.objects.filter(student=student, resolved=False).count(),
        'resolved_questions': Question.objects.filter(student=student, resolved=True).count(),
        'answers_given': Answer.objects.filter(user=student).count(),
        'good_answers': Answer.objects.filter(user=student, good=True).count(),
    }
    return render(request, 'users/profile_student.html', context)

@login_required
def view_student_profile(request, student_id, subject_id):
    student = get_object_or_404(CustomUser, id=student_id, role='student')
    context = {
        'student': student,
        'total_questions': Question.objects.filter(student=student).count(),
        'good_questions': Question.objects.filter(student=student, good=True).count(),
        'unresolved_questions': Question.objects.filter(student=student, resolved=False).count(),
        'resolved_questions': Question.objects.filter(student=student, resolved=True).count(),
        'answers_given': Answer.objects.filter(user=student).count(),
        'good_answers': Answer.objects.filter(user=student, good=True).count(),
        'subject_id': subject_id,
    }
    return render(request, 'users/profile_student_view.html', context)

@login_required
def student_subject_selection(request, view_type):
    subjects = StudentSubject.objects.filter(student=request.user)
    context = {'subjects': subjects, 'view_type': view_type}
    return render(request, 'users/student_subject_selection.html', context)

# users/views.py
from django.utils import timezone
from datetime import timedelta

@login_required
def student_subject_questions(request, subject_id, view_type):
    student = request.user
    subject = get_object_or_404(StudentSubject, id=subject_id, student=request.user)
    
    # Calculate deletion threshold (10 days)
    deletion_threshold = timezone.now() - timedelta(days=10)
    
    if view_type == 'resolved':
        # Get both general and good resolved questions
        general_questions = Question.objects.filter(
            student=student,
            subject=subject.subject,
            resolved=True,
            good=False
        )
        good_questions = Question.objects.filter(
            student=student,
            subject=subject.subject,
            resolved=True,
            good=True
        )
        
        # Add days left for deletion to general questions
        for q in general_questions:
            days_left = 10 - (timezone.now() - q.resolved_at).days
            q.days_left = max(0, days_left) if days_left > 0 else 0
            q.will_be_deleted = days_left <= 10 and days_left > 0
        
        context = {
            'subject': subject,
            'general_questions': general_questions,
            'good_questions': good_questions,
            'deletion_threshold': deletion_threshold,
            'view_type': view_type
        }
        return render(request, 'users/student_resolved_questions.html', context)
    
    else:
    
        if view_type == 'good_questions':
            questions = Question.objects.filter(
                student=student,
                subject=subject.subject,
                good=True
            )
            title = f"Good Questions - {subject}"

        elif view_type == 'unresolved':
            questions = Question.objects.filter(
                student=student,
                subject=subject.subject,
                resolved=False
            )
            title = f"Unresolved Questions - {subject}"
        
        else:
            questions = Question.objects.filter(
                student=student,
                subject=subject.subject
            )
            title = f"All Questions - {subject}"

        context = {
            'subject': subject,
            'questions': questions,
            'title': title,
            'view_type': view_type
        }
        return render(request, 'users/student_subject_questions.html', context)

@login_required
def student_answers(request, subject_id, answer_type):
    subject = get_object_or_404(StudentSubject, id=subject_id, student=request.user)
    student = request.user
    
    if answer_type == 'general_answers':
        answers = Answer.objects.filter(
            user=student,
            question__subject=subject.subject,
            good=False
        )
        title = f"General Answers - {subject}"
        
    elif answer_type == 'good_answers':
        answers = Answer.objects.filter(
            user=student,
            question__subject=subject.subject,
            good=True
        )
        title = f"Good Answers - {subject}"
    
    context = {
        'subject': subject,
        'answers': answers,
        'title': title,
        'answer_type': answer_type
    }
    return render(request, 'users/student_answers.html', context)