from django.db import models
from django.utils import timezone
from users.models import CustomUser

class YearGroup(models.Model):
    year = models.IntegerField(unique=True)
    
    def __str__(self):
        return f"Year {self.year}"

class Question(models.Model):
    title = models.CharField(max_length=200)
    tag = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='question_images/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    resolved = models.BooleanField(default=False)
    visible_to_teachers = models.BooleanField(default=False)
    year_group = models.ForeignKey(YearGroup, on_delete=models.CASCADE)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='questions')
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

class Answer(models.Model):
    text = models.TextField()
    image = models.ImageField(upload_to='answer_images/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    anonymous = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Answer to {self.question.title}"
    
    class Meta:
        ordering = ['created_at']