from django import forms
from .models import Question, Answer, TeacherSubject, StudentSubject, YearGroup, Subject
from users.models import CustomUser

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
        fields = ['text', 'image']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your answer here...'}),
        }
class TeacherSubjectForm(forms.ModelForm):
    class Meta:
        model = TeacherSubject
        fields = ['year', 'subject']
    
    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        self.fields['year'].queryset = YearGroup.objects.filter(year__in=range(8, 13))
        if teacher:
            existing_subjects = TeacherSubject.objects.filter(teacher=teacher).values_list('subject', flat=True)
            self.fields['subject'].queryset = Subject.objects.exclude(id__in=existing_subjects)

class StudentSubjectForm(forms.ModelForm):
    class Meta:
        model = StudentSubject
        fields = ['year', 'subject', 'teacher']

    def __init__(self, *args, **kwargs):
        student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)

        # Set year to student's year and make it not editable
        if student and student.year:
            year_instance = YearGroup.objects.get(year=student.year)
            self.fields['year'].initial = year_instance
            self.fields['year'].queryset = YearGroup.objects.filter(pk=year_instance.pk)
            self.fields['year'].disabled = True  # Make the field read-only

        # Filter teachers based on selected subject and year
        self.fields['teacher'].queryset = CustomUser.objects.none()

        if 'subject' in self.data and 'year' in self.data:
            try:
                year_id = int(self.data.get('year'))
                subject_id = int(self.data.get('subject'))
                self.fields['teacher'].queryset = CustomUser.objects.filter(
                    taught_subjects__year_id=year_id,
                    taught_subjects__subject_id=subject_id
                )
            except (ValueError, TypeError):
                pass