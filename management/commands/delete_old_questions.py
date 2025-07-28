from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from qa.models import Question

class Command(BaseCommand):
    help = 'Deletes resolved general questions older than 10 days'
    
    def handle(self, *args, **options):
        # Calculate the date 10 days ago
        threshold = timezone.now() - timedelta(days=10)
        
        # Find resolved general questions older than 10 days
        old_questions = Question.objects.filter(
            resolved=True,
            good=False,
            resolved_at__lte=threshold
        )
        
        # Delete them
        count = old_questions.count()
        old_questions.delete()
        
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} old resolved questions'))