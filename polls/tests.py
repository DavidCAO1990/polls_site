import datetime

from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse

from .models import Question

# Create your tests here.


class QuestionMethodTests(TestCase):
    """
    was_published_recently should return false for questions whose pub_date is in the future
    """

    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertEqual(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_pulished_recently should return false for questions whose pub_date is older than 1 day
        """
        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=time)
        self.assertEqual(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently should return true for questions whose pub_date is within 1 day
        """
        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date=time)
        self.assertEqual(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    Creates a question at any days from now
    :param question_text: content of the question to be published
    :param days: number of days offset to now, negative for the past and positive for the future
    :return: the Qestion instance
    """
    time = timezone.now() + datetime.timedelta(days)
    return Question.objects.create(question_text=question_text,
                                   pub_date=time)


class QuestionViewTests(TestCase):
    def test_index_view_with_no_questions(self):
        """
        If no questions exit, display a message
        :return:
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available currently.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_past_question(self):
        """
        Questions with a pub_date in the past should be displayed on the index page
        :return:
        """
        create_question(question_text="Past question", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question>']
        )

    def test_index_view_with_a_future_question(self):
        """
        Questions with a pub_date in the future should not be displayed in the index page
        :return:
        """
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available currently.",
                            status_code=200)
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                 [])

    def test_indext_view_with_future_and_past_questions(self):
        """
        For the cases where both past and future questions exit, only the past questions will be displayed
        :return:
        """
        create_question(question_text="Past question", days=-30)
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question>']
        )

    def test_indext_view_with_two_past_questions(self):
        """
        If more than one past questions exit, all of them should be displayed
        :return:
        """
        create_question(question_text="Past question 1", days=-30)
        create_question(question_text="Past question 2", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2>', '<Question: Past question 1>']
        )


class QuestionIndexDetailTests(TestCase):
    def test_detail_view_with_a_future_question(self):
        """
        the detail view for a question in the future should return a 404 not found error
        :return:
        """
        future_question = create_question(question_text='Future question.', days=5)
        response = self.client.get(reverse('polls:detail',
                                           args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question(self):
        """
        the detail view for a published question should display its content
        :return:
        """
        past_question = create_question(question_text='Past question.',
                                        days=-5)
        response = self.client.get(reverse('polls:detail',
                                           args=(past_question.id,)))
        self.assertContains(response, past_question.question_text, status_code=200)
