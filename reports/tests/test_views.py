from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from reports.models import Report


class ReportListFilterTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        settings.SECRET_KEY = 'test-secret'
        cls.user = get_user_model().objects.create_user(
            username='report-tester',
            password='password',
        )
        cls.target_report = Report.objects.create(host='target.example.org')
        Report.objects.create(host='other.example.org')

    def test_host_id_filter_returns_expected_reports(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('reports:report_list'),
            {'host_id': self.target_report.host},
        )

        self.assertEqual(response.status_code, 200)
        reports = list(response.context['page'].object_list)

        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0].pk, self.target_report.pk)
