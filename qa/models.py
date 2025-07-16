from django.db import models
from django.utils import timezone
from users.models import CustomUser

class YearGroup(models.Model):
    year = models.IntegerField(unique=True)
    
    def __str__(self):
        return f"Year {self.year}"
    
class Subject(models.Model):
    SUBJECT_CHOICES = [
        ('IG_Maths', 'IG Maths'),
        ('ESL', 'English as Second Language'),
        ('CFL', 'Chinese as First Language'),
        ('IG_Bio', 'IG Biology'),
        ('IG_Chem', 'IG Chemistry'),
        ('IG_Phy', 'IG Physics'),
        ('IG_Hist', 'IG History'),
        ('IG_Geo', 'IG Geography'),
        ('IG_Econ', 'IG Economics'),
        ('IG_Acc', 'IG Accounting'),
        ('IG_CS', 'IG Computer Science'),
        ('IG_Socio', 'IG Sociology'),
        ('IG_Bus', 'IG Business Studies'),
        ('AS_Bio', 'AS Biology'),
        ('AS_Chem', 'AS Chemistry'),
        ('AS_Phy', 'AS Physics'),
        ('AS_PM1', 'AS Pure Maths 1'),
        ('AS_PM2', 'AS Pure Maths 2'),
        ('AS_Mech1', 'AS Mechanics 1'),
        ('AS_Prob1', 'AS Prob & Stats 1'),
        ('AS_Econ', 'AS Economics'),
        ('AS_Acc', 'AS Accounting'),
        ('AS_CS', 'AS Computer Science'),
        ('AS_Socio', 'AS Sociology'),
        ('AS_Hist', 'AS History'),
        ('AS_Geo', 'AS Geography'),
        ('AS_Bus', 'AS Business Studies'),
        ('EFL', 'English as First Language'),
        ('FP1', 'Edexcel FP1'),
        ('FP2', 'Edexcel FP2'),
        ('DM1', 'Edexcel Decision Maths 1'),
        ('A2_Bio', 'A2 Biology'),
        ('A2_Chem', 'A2 Chemistry'),
        ('A2_Phy', 'A2 Physics'),
        ('A2_PM3', 'A2 Pure Maths 3'),
        ('A2_Mech2', 'A2 Mechanics 2'),
        ('A2_Prob2', 'A2 Prob & Stats 2'),
        ('A2_Econ', 'A2 Economics'),
        ('A2_Acc', 'A2 Accounting'),
        ('A2_CS', 'A2 Computer Science'),
        ('A2_Socio', 'A2 Sociology'),
        ('A2_Hist', 'A2 History'),
        ('A2_Geo', 'A2 Geography'),
        ('A2_Bus', 'A2 Business Studies'),
        ('Eng_Lit', 'English Literature'),
        ('FP3', 'Edexcel FP3'),
        ('FS1', 'Edexcel Further Stats 1'),
        ('FM1', 'Edexcel Further Mech 1'),
    ]
    
    name = models.CharField(max_length=100, choices=SUBJECT_CHOICES, unique=True)
    
    def __str__(self):
        return self.get_name_display()
    
class TeacherSubject(models.Model):
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='taught_subjects')
    year = models.ForeignKey(YearGroup, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('teacher', 'year', 'subject')
    
    def __str__(self):
        return f"Year {self.year.year} {self.subject}"

class StudentSubject(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='enrolled_subjects')
    year = models.ForeignKey(YearGroup, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='students_taught')
    
    class Meta:
        unique_together = ('student', 'year', 'subject')
    
    def __str__(self):
        return f"{self.subject} (Taught by: {self.teacher.real_name})"
    
class Question(models.Model):
    title = models.CharField(max_length=200)
    tag = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='question_images/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    resolved = models.BooleanField(default=False)
    visible_to_teachers = models.BooleanField(default=False)
    year_group = models.ForeignKey(YearGroup, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='questions')
    
    def __str__(self):
        return self.title
    
    def can_edit_delete(self, user):
        """Check if the user can edit or delete this question."""
        return user == self.student or user.role == 'teacher'
    
    class Meta:
        ordering = ['-created_at']

class Answer(models.Model):
    text = models.TextField()
    image = models.ImageField(upload_to='answer_images/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Answer to {self.question.title}"
    
    def can_edit_delete(self, user):
        """Check if the user can edit or delete this answer."""
        return user == self.user or user.role == 'teacher'
    
    class Meta:
        ordering = ['-created_at']