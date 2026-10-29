from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from companies.models import Company
from jobs.models import Job
from applications.models import JobApplication
from .models import ContactMessage

User = get_user_model()


class SecurityAndCoreTests(TestCase):
    """
    Security verification test suite:
    - Contact Message submission & validation
    - SQL Injection protection in search queries
    - XSS escaping in templates
    - Custom error handlers (404, 403)
    - Resume access control (IDOR prevention on resume download)
    """

    def setUp(self):
        self.client = Client()

        # Users
        self.recruiter = User.objects.create_user(
            username='auth_recruiter',
            email='recruiter@cyber.com',
            password='Password@123',
            role=User.ROLE_EMPLOYER
        )
        self.other_user = User.objects.create_user(
            username='random_intruder',
            email='intruder@hack.com',
            password='Password@123',
            role=User.ROLE_JOB_SEEKER
        )
        self.legit_applicant = User.objects.create_user(
            username='legit_applicant',
            email='legit@example.com',
            password='Password@123',
            role=User.ROLE_JOB_SEEKER
        )

        # Company & Job
        self.company = Company.objects.create(
            employer=self.recruiter,
            company_name='CyberShield Global',
            description='Cybersecurity solutions provider.',
            location='Bengaluru'
        )
        self.job = Job.objects.create(
            company=self.company,
            created_by=self.recruiter,
            title='Security Analyst',
            category='cybersecurity',
            status='PUBLISHED',
            location='Bengaluru',
            description='Protect enterprise assets.',
            required_skills='SIEM, Python, Network Security'
        )

        # Application with resume
        self.application = JobApplication.objects.create(
            job=self.job,
            applicant=self.legit_applicant,
            resume=SimpleUploadedFile("applicant_resume.pdf", b"%PDF-1.4 confidential applicant cv", content_type="application/pdf"),
            status=JobApplication.STATUS_APPLIED
        )

    def test_contact_form_submission_success(self):
        """Visitors can send valid contact inquiries."""
        response = self.client.post(reverse('core:contact'), {
            'name': 'Sarah Connor',
            'email': 'sarah@resistance.com',
            'subject': 'Enterprise Inquiries',
            'message': 'We want to post multiple jobs on your platform.',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ContactMessage.objects.filter(email='sarah@resistance.com').exists())

    def test_contact_form_invalid_email_fails(self):
        """Contact form with malformed email is rejected by server-side validation."""
        response = self.client.post(reverse('core:contact'), {
            'name': 'Bad Email User',
            'email': 'not-an-email',
            'subject': 'Help',
            'message': 'Test message.',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'email', 'Enter a valid email address.')

    def test_sql_injection_defense_in_search(self):
        """Searching with malicious SQL injection payloads is safely sanitized by Django ORM."""
        payloads = [
            "' OR '1'='1",
            "'; DROP TABLE jobs_job; --",
            "admin' --",
            "1 UNION SELECT 1,2,3,4,5"
        ]
        for payload in payloads:
            response = self.client.get(reverse('jobs:job_list'), {'q': payload})
            self.assertEqual(response.status_code, 200)
            # The database table still exists and query handled safely
            self.assertTrue(Job.objects.filter(pk=self.job.pk).exists())

    def test_xss_prevention_in_template_escaping(self):
        """Injected script tags are escaped safely by Django template engine."""
        xss_job = Job.objects.create(
            company=self.company,
            created_by=self.recruiter,
            title='<script>alert("XSS")</script> QA Tester',
            category='software',
            status='PUBLISHED',
            location='Remote',
            description='<img src=x onerror=alert(1)> description',
            required_skills='Testing'
        )
        response = self.client.get(reverse('jobs:job_detail', kwargs={'pk': xss_job.pk}))
        self.assertEqual(response.status_code, 200)
        # Verify literal script tag is escaped as &lt;script&gt; and not executed
        self.assertContains(response, '&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;')

    def test_resume_download_authorized_applicant(self):
        """The applicant can securely download their own submitted resume."""
        self.client.login(username='legit_applicant', password='Password@123')
        response = self.client.get(reverse('applications:download_resume', kwargs={'pk': self.application.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_resume_download_authorized_recruiter(self):
        """The recruiter who posted the job can download the applicant's resume."""
        self.client.login(username='auth_recruiter', password='Password@123')
        response = self.client.get(reverse('applications:download_resume', kwargs={'pk': self.application.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_resume_download_unauthorized_user_blocked(self):
        """An unauthorized third-party user cannot download another candidate's resume (returns 403)."""
        self.client.login(username='random_intruder', password='Password@123')
        response = self.client.get(reverse('applications:download_resume', kwargs={'pk': self.application.pk}))
        self.assertEqual(response.status_code, 403)
