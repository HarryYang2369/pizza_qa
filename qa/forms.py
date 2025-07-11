from django import forms
from .models import Question, Answer

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'tag', 'description', 'image', 'visible_to_teachers']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your question in detail...'}),
            'tag': forms.TextInput(attrs={'placeholder': 'e.g., Math, Science, History...'}),
        }
        labels = {
            'visible_to_teachers': 'Make visible to teachers only'
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'image', 'anonymous']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your answer here...'}),
        }
        labels = {
            'anonymous': 'Post anonymously'
        }