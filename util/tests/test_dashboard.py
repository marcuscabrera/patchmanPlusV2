from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse

from arch.models import MachineArchitecture
from repos.models import Mirror, Repository


class DashboardMirrorStatusTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        settings.SECRET_KEY = 'test-secret'

        Site.objects.update_or_create(
            id=1,
            defaults={
                'domain': 'example.com',
                'name': 'Example',
            },
        )

        cls.arch = MachineArchitecture.objects.create(name='x86_64')

        cls.mixed_repo = Repository.objects.create(
            name='mixed-repo',
            arch=cls.arch,
            repotype=Repository.RPM,
        )
        Mirror.objects.create(
            repo=cls.mixed_repo,
            url='http://mirror.example.com/fail',
            last_access_ok=False,
        )
        Mirror.objects.create(
            repo=cls.mixed_repo,
            url='http://mirror.example.com/success',
            last_access_ok=True,
        )

        cls.failed_repo = Repository.objects.create(
            name='failed-repo',
            arch=cls.arch,
            repotype=Repository.RPM,
        )
        Mirror.objects.create(
            repo=cls.failed_repo,
            url='http://mirror.example.com/failed-1',
            last_access_ok=False,
        )
        Mirror.objects.create(
            repo=cls.failed_repo,
            url='http://mirror.example.com/failed-2',
            last_access_ok=False,
        )

        cls.success_repo = Repository.objects.create(
            name='success-repo',
            arch=cls.arch,
            repotype=Repository.RPM,
        )
        Mirror.objects.create(
            repo=cls.success_repo,
            url='http://mirror.example.com/success-only',
            last_access_ok=True,
        )

        cls.auth_repo = Repository.objects.create(
            name='auth-repo',
            arch=cls.arch,
            repotype=Repository.RPM,
            auth_required=True,
        )
        Mirror.objects.create(
            repo=cls.auth_repo,
            url='http://mirror.example.com/auth-fail',
            last_access_ok=False,
        )

        cls.user = get_user_model().objects.create_user(
            username='tester',
            password='password',
        )

    def test_mixed_and_failed_repositories_categorised_correctly(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('util:dashboard'))

        failed_mirrors = response.context['failed_mirrors']
        failed_repos = response.context['failed_repos']

        self.assertTrue(
            failed_mirrors.filter(pk=self.mixed_repo.pk).exists(),
            'Repositories with mixed mirror status should appear under failed_mirrors',
        )
        self.assertFalse(
            failed_repos.filter(pk=self.mixed_repo.pk).exists(),
            'Repositories with both working and failing mirrors must not be treated as fully failed',
        )

        self.assertTrue(
            failed_repos.filter(pk=self.failed_repo.pk).exists(),
            'Repositories where all mirrors fail should appear under failed_repos',
        )
        self.assertFalse(
            failed_mirrors.filter(pk=self.failed_repo.pk).exists(),
            'Repositories where all mirrors fail should not appear under partially failed mirrors',
        )

        self.assertFalse(
            failed_mirrors.filter(pk=self.success_repo.pk).exists(),
            'Repositories with only successful mirrors should not be flagged as failed',
        )
        self.assertFalse(
            failed_repos.filter(pk=self.success_repo.pk).exists(),
            'Repositories with only successful mirrors should not be flagged as fully failed',
        )

        self.assertFalse(
            failed_mirrors.filter(pk=self.auth_repo.pk).exists(),
            'Repositories requiring auth should be excluded from mirror failure checks',
        )
        self.assertFalse(
            failed_repos.filter(pk=self.auth_repo.pk).exists(),
            'Repositories requiring auth should be excluded from mirror failure checks',
        )

