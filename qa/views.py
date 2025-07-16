from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import YearGroup, Question, Answer, TeacherSubject, StudentSubject
from .forms import QuestionForm, AnswerForm, TeacherSubjectForm, StudentSubjectForm, Subject
from django.http import JsonResponse

# @login_required
# def year_selection(request):
#     years = YearGroup.objects.all()
#     return render(request, 'qa/year_selection.html', {'years': years})

# @login_required
# def class_qa(request, year_id):
#     year = get_object_or_404(YearGroup, id=year_id)
    
#     if request.user.role == 'student':
#         # Show: 
#         # 1. Public questions (visible_to_teachers=False)
#         # 2. Teacher-only questions that belong to the current student
#         questions = Question.objects.filter(
#             Q(year_group=year) &
#             (Q(visible_to_teachers=False) | 
#              Q(visible_to_teachers=True, student=request.user))
#         ).order_by('-created_at')
#     else:
#         # Teachers see all questions
#         questions = Question.objects.filter(year_group=year).order_by('-created_at')
    
#     context = {'year': year, 'questions': questions}
#     return render(request, 'qa/class_qa.html', context)

@login_required
def ask_question(request, subject_id):
    subject = get_object_or_404(StudentSubject, id=subject_id, student=request.user)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.student = request.user
            question.subject = subject.subject
            question.year_group = subject.year
            question.save()
            messages.success(request, "Your question has been posted!")
            return redirect('qa:subject_qa', subject_id=subject.id)
    else:
        form = QuestionForm()
    
    context = {'form': form, 'subject': subject}
    return render(request, 'qa/ask_question.html', context)

@login_required
def question_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.user.role == 'teacher':
        subject = get_object_or_404(TeacherSubject, subject=question.subject, teacher=request.user)
    else:
        subject = get_object_or_404(StudentSubject, subject=question.subject, student=request.user)
    # Security check: Students can only see their own teacher-only questions
    if request.user.role == 'student' and question.visible_to_teachers and question.student!= request.user:
        if question.student != request.user:
            messages.error(request, "You don't have permission to view this question.")
            return redirect('qa:subject_selection')
    
    answers = question.answers.all()
    form = AnswerForm()
    
    if request.method == 'POST':
        form = AnswerForm(request.POST, request.FILES)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.user = request.user
            answer.save()
            messages.success(request, "Your answer has been posted!")
            return redirect('qa:question_detail', question_id=question_id)
    
    context = {
        'question': question,
        'answers': answers,
        'form': form,
        'subject': subject
    }
    return render(request, 'qa/question_detail.html', context)

@login_required
def mark_resolved(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    # Only student who asked or teacher can mark resolved
    if request.user == question.student or request.user.role == 'teacher':
        question.resolved = not question.resolved
        question.save()
        status = "resolved" if question.resolved else "unresolved"
        messages.success(request, f"Question marked as {status}!")
    
    return redirect('qa:question_detail', question_id=question_id)

@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    # Permission check
    if not question.can_edit_delete(request.user):
        messages.error(request, "You don't have permission to edit this question.")
        return redirect('qa:question_detail', question_id=question_id)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, "Question updated successfully!")
            return redirect('qa:question_detail', question_id=question_id)
    else:
        form = QuestionForm(instance=question)
    
    context = {'form': form, 'question': question}
    return render(request, 'qa/edit_question.html', context)

@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    # Permission check
    if not question.can_edit_delete(request.user):
        messages.error(request, "You don't have permission to delete this question.")
        return redirect('qa:question_detail', question_id=question_id)
    
    if request.method == 'POST':
        year_id = question.year_group.id
        question.delete()
        messages.success(request, "Question has been deleted.")
        return redirect('qa:subject_qa', year_id=year_id)
    
    context = {'question': question}
    return render(request, 'qa/confirm_delete_question.html', context)

@login_required
def edit_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    question = answer.question
    
    # Permission check
    if not answer.can_edit_delete(request.user):
        messages.error(request, "You don't have permission to edit this answer.")
        return redirect('qa:question_detail', question_id=question.id)
    
    if request.method == 'POST':
        form = AnswerForm(request.POST, request.FILES, instance=answer)
        if form.is_valid():
            form.save()
            messages.success(request, "Answer updated successfully!")
            return redirect('qa:question_detail', question_id=question.id)
    else:
        form = AnswerForm(instance=answer)
    
    context = {'form': form, 'answer': answer, 'question': question}
    return render(request, 'qa/edit_answer.html', context)

@login_required
def delete_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    question = answer.question
    
    # Permission check
    if not answer.can_edit_delete(request.user):
        messages.error(request, "You don't have permission to delete this answer.")
        return redirect('qa:question_detail', question_id=question.id)
    
    if request.method == 'POST':
        answer.delete()
        messages.success(request, "Answer has been deleted.")
        return redirect('qa:question_detail', question_id=question.id)
    
    context = {'answer': answer, 'question': question}
    return render(request, 'qa/confirm_delete_answer.html', context)

@login_required
def manage_teacher_subjects(request):
    """Teacher subject management view"""
    if request.user.role != 'teacher':
        return redirect('qa:subject_selection')
    
    # Handle subject deletion
    if request.method == 'POST' and 'delete_subject' in request.POST:
        subject_id = request.POST.get('delete_subject')
        subject = get_object_or_404(TeacherSubject, id=subject_id, teacher=request.user)
        subject.delete()
        messages.success(request, "Subject removed successfully!")
        return redirect('qa:manage_teacher_subjects')
    
    # Add new subject form
    form = TeacherSubjectForm(teacher=request.user)
    if request.method == 'POST' and 'add_subject' in request.POST:
        form = TeacherSubjectForm(request.POST, teacher=request.user)
        if form.is_valid():
            teacher_subject = form.save(commit=False)
            teacher_subject.teacher = request.user
            teacher_subject.save()
            messages.success(request, "Subject added successfully!")
            return redirect('qa:manage_teacher_subjects')
    
    # Get teacher's current subjects
    current_subjects = TeacherSubject.objects.filter(teacher=request.user)
    
    context = {
        'form': form,
        'current_subjects': current_subjects
    }
    return render(request, 'qa/manage_teacher_subjects.html', context)

@login_required
def manage_student_subjects(request):
    """Student subject management view"""
    if request.user.role != 'student':
        return redirect('qa:subject_selection')
    
    # Handle subject deletion
    if request.method == 'POST' and 'delete_subject' in request.POST:
        subject_id = request.POST.get('delete_subject')
        subject = get_object_or_404(StudentSubject, id=subject_id, student=request.user)
        subject.delete()
        messages.success(request, "Subject removed successfully!")
        return redirect('qa:manage_student_subjects')
    
    # Add new subject form
    form = StudentSubjectForm(student=request.user)
    if request.method == 'POST' and 'add_subject' in request.POST:
        form = StudentSubjectForm(request.POST, student=request.user)
        if form.is_valid():
            student_subject = form.save(commit=False)
            student_subject.student = request.user
            student_subject.save()
            messages.success(request, "Subject added successfully!")
            return redirect('qa:manage_student_subjects')
    
    # Get student's current subjects
    current_subjects = StudentSubject.objects.filter(student=request.user)
    
    context = {
        'form': form,
        'current_subjects': current_subjects
    }
    return render(request, 'qa/manage_student_subjects.html', context)

@login_required
def subject_selection(request):
    """Show subjects available to the current user"""
    subjects = request.user.get_available_subjects()
    
    context = {'subjects': subjects}
    return render(request, 'qa/subject_selection.html', context)

@login_required
def subject_qa(request, subject_id):
    """Show questions for a specific subject"""
    if request.user.role == 'teacher':
        subject = get_object_or_404(TeacherSubject, id=subject_id, teacher=request.user)
    else:
        subject = get_object_or_404(StudentSubject, id=subject_id, student=request.user)
    
    # Get questions for this subject and year
    questions = Question.objects.filter(
        subject=subject.subject,
        
    ).order_by('-created_at')
    
    context = {
        'subject': subject,
        'questions': questions
    }
    return render(request, 'qa/subject_qa.html', context)

def get_teachers(request):
    """API endpoint to get teachers for a specific year and subject"""
    year_id = request.GET.get('year')
    subject_id = request.GET.get('subject')
    
    if not year_id or not subject_id:
        return JsonResponse({'teachers': []})
    
    try:
        year = YearGroup.objects.get(id=year_id)
        subject = Subject.objects.get(id=subject_id)
        
        # Get teachers who teach this subject in this year
        teachers = TeacherSubject.objects.filter(
            year=year,
            subject=subject
        ).select_related('teacher')
        
        teacher_data = [{
            'id': ts.teacher.id,
            'name': ts.teacher.real_name
        } for ts in teachers]
        
        return JsonResponse({'teachers': teacher_data})
    
    except (YearGroup.DoesNotExist, Subject.DoesNotExist):
        return JsonResponse({'teachers': []})
