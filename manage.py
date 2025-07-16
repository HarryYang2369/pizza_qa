#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pizza_qa.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()


# >>> from qa.models import YearGroup
# >>> for year in range(8, 13):
# ...     YearGroup.objects.get_or_create(year=year)
# ... 
# (<YearGroup: Year 8>, True)
# (<YearGroup: Year 9>, False)
# (<YearGroup: Year 10>, False)
# (<YearGroup: Year 11>, False)
# (<YearGroup: Year 12>, False)
# >>> from qa.models import Subject
# >>> subjects = ['IG Maths', 'English as Second Language', 'Chinese as First Language', 'IG Biology', 'IG Chemistry', 'IG Physics', 'IG History', 'IG Geography', 'IG Economics', 'IG Accounting', 'IG Computer Science', 'IG Sociology', 'IG Business Studies', 'AS Biology', 'AS Chemistry', 'AS Physics', 'AS Pure Maths 1', 'AS Pure Maths 2', 'AS Mechanics 1', 'AS Prob & Stats 1', 'AS Economics', 'AS Accounting', 'AS Computer Science', 'AS Sociology', 'AS History', 'AS Geography', 'AS Business Studies', 'English as First Language', 'Edexcel FP1', 'Edexcel FP2', 'Edexcel Decision Maths 1', 'A2 Biology', 'A2 Chemistry', 'A2 Physics', 'A2 Pure Maths 3', 'A2 Mechanics 2', 'A2 Prob & Stats 2', 'A2 Economics', 'A2 Accounting', 'A2 Computer Science', 'A2 Sociology', 'A2 History', 'A2 Geography', 'A2 Business Studies', 'English Literature', 'Edexcel FP3', 'Edexcel Further Stats 1', 'Edexcel Further Mech 1']
# >>> for subject in subjects:
# ...     Subject.objects.get_or_create(name=subject)
# ... 