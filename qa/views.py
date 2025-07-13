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
    
    if request.user.role == 'student':
        # Show: 
        # 1. Public questions (visible_to_teachers=False)
        # 2. Teacher-only questions that belong to the current student
        questions = Question.objects.filter(
            Q(year_group=year) &
            (Q(visible_to_teachers=False) | 
             Q(visible_to_teachers=True, student=request.user))
        ).order_by('-created_at')
    else:
        # Teachers see all questions
        questions = Question.objects.filter(year_group=year).order_by('-created_at')
    
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
    if request.user.role == 'student' and question.visible_to_teachers and question.student!= request.user:
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
        return redirect('qa:class_qa', year_id=year_id)
    
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