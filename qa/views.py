from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import YearGroup, Question, Answer
from .forms import QuestionForm, AnswerForm

@login_required
def year_selection(request):
    years = YearGroup.objects.all()
    return render(request, 'qa/year_selection.html', {'years': years})

@login_required
def class_qa(request, year_id):
    year = get_object_or_404(YearGroup, id=year_id)
    
    # Students can only see non-teacher-only questions in their year
    # Teachers can see all questions
    if request.user.role == 'student':
        questions = Question.objects.filter(
            year_group=year,
            visible_to_teachers=False
        )
    else:
        questions = Question.objects.filter(year_group=year)
    
    context = {'year': year, 'questions': questions}
    return render(request, 'qa/class_qa.html', context)

@login_required
def ask_question(request, year_id):
    year = get_object_or_404(YearGroup, id=year_id)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.student = request.user
            question.year_group = year
            question.save()
            messages.success(request, "Your question has been posted!")
            return redirect('qa:class_qa', year_id=year_id)
    else:
        form = QuestionForm()
    
    context = {'form': form, 'year': year}
    return render(request, 'qa/ask_question.html', context)

@login_required
def question_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    # Security check: Students can only see their own teacher-only questions
    if request.user.role == 'student' and question.visible_to_teachers:
        if question.student != request.user:
            messages.error(request, "You don't have permission to view this question.")
            return redirect('qa:year_selection')
    
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
        'form': form
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
    
    # Only the student who asked can edit
    if request.user != question.student:
        messages.error(request, "You can only edit your own questions.")
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

# When I logged in as student, I try to click Ask Question button. It does not work in any year section. After clicking the button it always shows [11/Jul/2025 09:18:54] "GET /qa/ask/3/ HTTP/1.1" 200 3656 and keep on the same page after a flicker, is there something with the ask_question.html or ask_question() function in views.html?