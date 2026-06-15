from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser
from .models import (
    YearGroup, Subject, TeacherSubject, StudentSubject,
    Question, Answer, Followup, Notification,
)


class QAFlowTests(TestCase):
    def setUp(self):
        self.year = YearGroup.objects.create(year=11)
        self.subject = Subject.objects.create(name='IG_Maths')

        self.teacher = CustomUser.objects.create_user(
            email='teacher@school.edu', password='pass12345',
            real_name='Tina Teacher', role='teacher',
        )
        self.student = CustomUser.objects.create_user(
            email='student@school.edu', password='pass12345',
            real_name='Sam Student', role='student', year=11,
        )

        self.teacher_subject = TeacherSubject.objects.create(
            teacher=self.teacher, year=self.year, subject=self.subject,
        )
        self.student_subject = StudentSubject.objects.create(
            student=self.student, year=self.year, subject=self.subject,
            teacher=self.teacher,
        )
        self.question = Question.objects.create(
            title='Quadratic help', tag='algebra',
            description='How do I complete the square?',
            year_group=self.year, subject=self.subject, student=self.student,
        )

    def test_answer_creates_notification_for_asker(self):
        self.client.force_login(self.teacher)
        resp = self.client.post(
            reverse('qa:question_detail', args=[self.question.id]),
            {'text': 'Use the formula (x + b/2)^2.'},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Answer.objects.count(), 1)
        note = Notification.objects.get(recipient=self.student)
        self.assertIn('answered your question', note.message)
        self.assertFalse(note.is_read)

    def test_followup_and_reply_notifications(self):
        # Student posts a follow-up -> no notification to self
        self.client.force_login(self.student)
        self.client.post(
            reverse('qa:add_followup', args=[self.question.id]),
            {'text': 'Still confused about step 2.'},
        )
        followup = Followup.objects.get()
        self.assertIsNone(followup.parent)
        self.assertEqual(Notification.objects.filter(recipient=self.student).count(), 0)

        # Teacher replies -> student gets notified
        self.client.force_login(self.teacher)
        self.client.post(
            reverse('qa:add_followup', args=[self.question.id]),
            {'text': 'Step 2: halve the coefficient.', 'parent_id': followup.id},
        )
        reply = Followup.objects.get(parent=followup)
        self.assertEqual(reply.parent, followup)
        self.assertTrue(
            Notification.objects.filter(recipient=self.student).exists()
        )

    def test_reply_to_reply_stays_one_level(self):
        top = Followup.objects.create(
            question=self.question, user=self.student, text='top',
        )
        reply = Followup.objects.create(
            question=self.question, user=self.teacher, text='reply', parent=top,
        )
        self.client.force_login(self.student)
        self.client.post(
            reverse('qa:add_followup', args=[self.question.id]),
            {'text': 'reply to a reply', 'parent_id': reply.id},
        )
        newest = Followup.objects.latest('id')
        # Should attach to the top-level parent, not nest deeper
        self.assertEqual(newest.parent, top)

    def test_search_filters_questions(self):
        Question.objects.create(
            title='Photosynthesis', description='biology stuff',
            year_group=self.year, subject=self.subject, student=self.student,
        )
        self.client.force_login(self.student)
        url = reverse('qa:subject_qa', args=[self.student_subject.id])
        resp = self.client.get(url, {'q': 'quadratic'})
        self.assertContains(resp, 'Quadratic help')
        self.assertNotContains(resp, 'Photosynthesis')

    def test_status_filter_unanswered(self):
        answered = Question.objects.create(
            title='Answered Q', description='x',
            year_group=self.year, subject=self.subject, student=self.student,
        )
        Answer.objects.create(question=answered, user=self.teacher, text='done')
        self.client.force_login(self.student)
        url = reverse('qa:subject_qa', args=[self.student_subject.id])
        resp = self.client.get(url, {'status': 'unanswered'})
        self.assertContains(resp, 'Quadratic help')
        self.assertNotContains(resp, 'Answered Q')

    def test_student_cannot_see_others_teacher_only_question(self):
        other_student = CustomUser.objects.create_user(
            email='other@school.edu', password='pass12345',
            real_name='Olive Other', role='student', year=11,
        )
        StudentSubject.objects.create(
            student=other_student, year=self.year, subject=self.subject,
            teacher=self.teacher,
        )
        private_q = Question.objects.create(
            title='Private question', description='secret',
            visible_to_teachers=True,
            year_group=self.year, subject=self.subject, student=self.student,
        )
        self.client.force_login(other_student)
        resp = self.client.get(
            reverse('qa:question_detail', args=[private_q.id]), follow=True,
        )
        self.assertContains(resp, "permission to view this question")

    def test_notifications_mark_all_read(self):
        Notification.objects.create(
            recipient=self.student, message='hi', question=self.question,
        )
        self.client.force_login(self.student)
        self.client.post(reverse('qa:mark_all_read'))
        self.assertEqual(
            Notification.objects.filter(recipient=self.student, is_read=False).count(), 0
        )

    def test_delete_question_redirects_to_subjects(self):
        self.client.force_login(self.student)
        resp = self.client.post(
            reverse('qa:delete_question', args=[self.question.id])
        )
        self.assertRedirects(resp, reverse('qa:subject_selection'))
        self.assertEqual(Question.objects.count(), 0)
