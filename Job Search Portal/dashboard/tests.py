from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from companies.models import Company
from jobs.models import Job
from applications.models import JobApplication, SavedJob

User = get_user_model()


class DashboardAnalyticsTests(TestCase):
    """
    Test suite for Job Seeker Dashboard and Employer Dashboard analytics,
    profile completeness calculation, funnel metrics, and access control.
    """

    def setUp(self):
        self.client = Client()

        # Users
        self.employer = User.objects.create_user(
            username='boss_recruiter',
            email='boss@enterprise.com',
            password='Password@123',
            role=User.ROLE_EMPLOYER
        )
        self.job_seeker = User.objects.create_user(
            username='candidate_clara',
            email='clara@example.com',
            password='Password@123',
            role=User.ROLE_JOB_SEEKER
        )

        # Company
        self.company = Company.objects.create(
            employer=self.employer,
            company_name='Enterprise Tech Labs',
            description='Enterprise cloud computing company.',
            location='Pune, India'
        )

        # Job
        self.job = Job.objects.create(
            company=self.company,
            created_by=self.employer,
            title='Staff Software Engineer',
            category='software',
            job_type='full_time',
            status='PUBLISHED',
            location='Pune, India',
            description='Core platform architecture.',
            required_skills='Python, Django, MySQL, Kubernetes',
            application_deadline=timezone.now().date() + timedelta(days=30)
        )

        # Application
        self.application = JobApplication.objects.create(
            job=self.job,
            applicant=self.job_seeker,
            resume=SimpleUploadedFile("resume.pdf", b"%PDF-1.4 test", content_type="application/pdf"),
            status=JobApplication.STATUS_APPLIED
        )

        # Saved Job
        self.saved_job = SavedJob.objects.create(
            user=self.job_seeker,
            job=self.job
        )

    def test_dashboard_index_redirects_seeker(self):
        """Logged in job seeker visiting /dashboard/ is redirected to seeker dashboard."""
        self.client.login(username='candidate_clara', password='Password@123')
        response = self.client.get(reverse('dashboard:index'), follow=True)
        self.assertRedirects(response, reverse('dashboard:seeker_dashboard'))

    def test_dashboard_index_redirects_employer(self):
        """Logged in employer visiting /dashboard/ is redirected to employer dashboard."""
        self.client.login(username='boss_recruiter', password='Password@123')
        response = self.client.get(reverse('dashboard:index'), follow=True)
        self.assertRedirects(response, reverse('dashboard:employer_dashboard'))

    def test_seeker_dashboard_metrics(self):
        """Seeker dashboard displays metrics, completion rate, recent applications, and wishlist."""
        self.client.login(username='candidate_clara', password='Password@123')
        response = self.client.get(reverse('dashboard:seeker_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Staff Software Engineer')
        self.assertContains(response, 'Enterprise Tech Labs')
        self.assertContains(response, 'Total Applied')
        self.assertEqual(response.context['total_applied'], 1)
        self.assertEqual(response.context['total_saved'], 1)
        self.assertGreater(response.context['completion_score'], 0)

    def test_employer_dashboard_metrics(self):
        """Employer dashboard displays total jobs, active jobs, and received applications funnel."""
        self.client.login(username='boss_recruiter', password='Password@123')
        response = self.client.get(reverse('dashboard:employer_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enterprise Tech Labs')
        self.assertContains(response, 'Staff Software Engineer')
        self.assertEqual(response.context['total_jobs'], 1)
        self.assertEqual(response.context['active_jobs'], 1)
        self.assertEqual(response.context['total_applications'], 1)
        self.assertEqual(response.context['applied_count'], 1)

    def test_role_security_seeker_cannot_access_employer_dashboard(self):
        """Job seeker attempting to access employer dashboard gets redirected to seeker dashboard."""
        self.client.login(username='candidate_clara', password='Password@123')
        response = self.client.get(reverse('dashboard:employer_dashboard'), follow=True)
        self.assertRedirects(response, reverse('dashboard:seeker_dashboard'))

    def test_role_security_employer_cannot_access_seeker_dashboard(self):
        """Employer attempting to access seeker dashboard gets redirected to employer dashboard."""
        self.client.login(username='boss_recruiter', password='Password@123')
        response = self.client.get(reverse('dashboard:seeker_dashboard'), follow=True)
        self.assertRedirects(response, reverse('dashboard:employer_dashboard'))

    def test_anonymous_user_redirected_to_login(self):
        """Unauthenticated visitor is redirected to login page."""
        response = self.client.get(reverse('dashboard:seeker_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)
