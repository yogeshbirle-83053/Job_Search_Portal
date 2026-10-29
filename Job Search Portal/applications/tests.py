from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from companies.models import Company
from jobs.models import Job
from .models import JobApplication, SavedJob

User = get_user_model()


class JobApplicationAndWishlistTests(TestCase):
    """
    Test suite for job applications, duplicate prevention, resume snapshots,
    status updates, withdrawal rules, saved jobs wishlist, and IDOR access control.
    """

    def setUp(self):
        self.client = Client()

        # Users
        self.recruiter_a = User.objects.create_user(
            username='recruiter_a',
            email='recruiterA@corp.com',
            password='Password@123',
            role=User.ROLE_EMPLOYER
        )
        self.recruiter_b = User.objects.create_user(
            username='recruiter_b',
            email='recruiterB@corp.com',
            password='Password@123',
            role=User.ROLE_EMPLOYER
        )
        self.job_seeker = User.objects.create_user(
            username='seeker_dan',
            email='dan@example.com',
            password='Password@123',
            role=User.ROLE_JOB_SEEKER
        )

        # Upload initial profile resume for job seeker
        pdf_bytes = b"%PDF-1.4 sample profile resume for testing"
        self.job_seeker.seeker_profile.resume = SimpleUploadedFile("profile_cv.pdf", pdf_bytes, content_type="application/pdf")
        self.job_seeker.seeker_profile.save()

        # Company
        self.company = Company.objects.create(
            employer=self.recruiter_a,
            company_name='Nexus Systems',
            description='Enterprise solutions company.',
            location='Hyderabad'
        )

        # Job
        self.active_job = Job.objects.create(
            company=self.company,
            created_by=self.recruiter_a,
            title='Backend Python Engineer',
            category='software',
            job_type='full_time',
            status='PUBLISHED',
            location='Hyderabad',
            description='Seeking Python developer.',
            required_skills='Python, Django',
            application_deadline=timezone.now().date() + timedelta(days=30)
        )

        self.closed_job = Job.objects.create(
            company=self.company,
            created_by=self.recruiter_a,
            title='Closed Role',
            category='software',
            status='CLOSED',
            location='Hyderabad',
            description='Position has been closed.',
            required_skills='Python'
        )

    def test_apply_with_profile_resume(self):
        """Job seeker can apply using their existing profile resume."""
        self.client.login(username='seeker_dan', password='Password@123')
        response = self.client.post(reverse('applications:apply_job', kwargs={'job_id': self.active_job.pk}), {
            'resume_choice': 'profile',
            'cover_letter': 'I am thrilled to apply for this backend role.',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(JobApplication.objects.filter(job=self.active_job, applicant=self.job_seeker).exists())
        application = JobApplication.objects.get(job=self.active_job, applicant=self.job_seeker)
        self.assertEqual(application.status, JobApplication.STATUS_APPLIED)
        self.assertEqual(application.cover_letter, 'I am thrilled to apply for this backend role.')
        self.assertTrue(bool(application.resume))

    def test_apply_with_custom_uploaded_resume(self):
        """Job seeker can apply by uploading a custom tailored PDF resume."""
        self.client.login(username='seeker_dan', password='Password@123')
        custom_pdf = SimpleUploadedFile("tailored_cv.pdf", b"%PDF-1.4 custom resume content", content_type="application/pdf")

        response = self.client.post(reverse('applications:apply_job', kwargs={'job_id': self.active_job.pk}), {
            'resume_choice': 'upload',
            'custom_resume': custom_pdf,
            'cover_letter': 'Tailored cover letter.',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(JobApplication.objects.filter(job=self.active_job, applicant=self.job_seeker).exists())

    def test_duplicate_application_prevented_in_form(self):
        """Applying a second time to the same job is rejected by validation."""
        self.client.login(username='seeker_dan', password='Password@123')

        # First application
        JobApplication.objects.create(
            job=self.active_job,
            applicant=self.job_seeker,
            resume=SimpleUploadedFile("cv.pdf", b"%PDF-1.4 dummy", content_type="application/pdf"),
            status=JobApplication.STATUS_APPLIED
        )

        # Attempt second application
        response = self.client.post(reverse('applications:apply_job', kwargs={'job_id': self.active_job.pk}), {
            'resume_choice': 'profile',
        }, follow=True)

        # Redirected or form error
        self.assertEqual(response.status_code, 200)
        self.assertEqual(JobApplication.objects.filter(job=self.active_job, applicant=self.job_seeker).count(), 1)

    def test_duplicate_application_prevented_by_database_constraint(self):
        """Database constraint enforces uniqueness on (job, applicant)."""
        JobApplication.objects.create(
            job=self.active_job,
            applicant=self.job_seeker,
            resume=SimpleUploadedFile("cv1.pdf", b"%PDF-1.4 dummy", content_type="application/pdf"),
            status=JobApplication.STATUS_APPLIED
        )

        with self.assertRaises(IntegrityError):
            JobApplication.objects.create(
                job=self.active_job,
                applicant=self.job_seeker,
                resume=SimpleUploadedFile("cv2.pdf", b"%PDF-1.4 dummy", content_type="application/pdf"),
                status=JobApplication.STATUS_APPLIED
            )

    def test_cannot_apply_to_closed_job(self):
        """Applying to a closed job is blocked."""
        self.client.login(username='seeker_dan', password='Password@123')
        response = self.client.get(reverse('applications:apply_job', kwargs={'job_id': self.closed_job.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(JobApplication.objects.filter(job=self.closed_job, applicant=self.job_seeker).exists())

    def test_candidate_can_withdraw_eligible_application(self):
        """Job seeker can withdraw an application while it is still in APPLIED stage."""
        application = JobApplication.objects.create(
            job=self.active_job,
            applicant=self.job_seeker,
            resume=SimpleUploadedFile("cv.pdf", b"%PDF-1.4 dummy", content_type="application/pdf"),
            status=JobApplication.STATUS_APPLIED
        )

        self.client.login(username='seeker_dan', password='Password@123')
        response = self.client.get(reverse('applications:withdraw_application', kwargs={'pk': application.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(JobApplication.objects.filter(pk=application.pk).exists())

    def test_candidate_cannot_withdraw_shortlisted_application(self):
        """Job seeker cannot withdraw an application once it has progressed to SHORTLISTED."""
        application = JobApplication.objects.create(
            job=self.active_job,
            applicant=self.job_seeker,
            resume=SimpleUploadedFile("cv.pdf", b"%PDF-1.4 dummy", content_type="application/pdf"),
            status=JobApplication.STATUS_SHORTLISTED
        )

        self.client.login(username='seeker_dan', password='Password@123')
        response = self.client.get(reverse('applications:withdraw_application', kwargs={'pk': application.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(JobApplication.objects.filter(pk=application.pk).exists())

    def test_wishlist_toggle_saved_job(self):
        """Job seeker can bookmark and unbookmark jobs in wishlist."""
        self.client.login(username='seeker_dan', password='Password@123')

        # Bookmark
        response1 = self.client.get(reverse('applications:toggle_save_job', kwargs={'job_id': self.active_job.pk}), follow=True)
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(SavedJob.objects.filter(user=self.job_seeker, job=self.active_job).exists())

        # Unbookmark
        response2 = self.client.get(reverse('applications:toggle_save_job', kwargs={'job_id': self.active_job.pk}), follow=True)
        self.assertEqual(response2.status_code, 200)
        self.assertFalse(SavedJob.objects.filter(user=self.job_seeker, job=self.active_job).exists())

    def test_employer_can_view_and_update_applicant_status(self):
        """Employer can review application and transition status to SHORTLISTED."""
        application = JobApplication.objects.create(
            job=self.active_job,
            applicant=self.job_seeker,
            resume=SimpleUploadedFile("cv.pdf", b"%PDF-1.4 dummy", content_type="application/pdf"),
            status=JobApplication.STATUS_APPLIED
        )

        self.client.login(username='recruiter_a', password='Password@123')

        # View job applicants list
        response = self.client.get(reverse('applications:job_applicants', kwargs={'job_id': self.active_job.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'seeker_dan')

        # Update status
        update_response = self.client.post(reverse('applications:applicant_detail', kwargs={'pk': application.pk}), {
            'status': JobApplication.STATUS_SHORTLISTED
        }, follow=True)
        self.assertEqual(update_response.status_code, 200)
        application.refresh_from_db()
        self.assertEqual(application.status, JobApplication.STATUS_SHORTLISTED)

    def test_idor_protection_employer_cannot_view_other_job_applicants(self):
        """Employer B cannot view applicants or update status of Employer A's job (returns 404)."""
        application = JobApplication.objects.create(
            job=self.active_job,
            applicant=self.job_seeker,
            resume=SimpleUploadedFile("cv.pdf", b"%PDF-1.4 dummy", content_type="application/pdf"),
            status=JobApplication.STATUS_APPLIED
        )

        self.client.login(username='recruiter_b', password='Password@123')

        # Attempt to access applicants list
        res1 = self.client.get(reverse('applications:job_applicants', kwargs={'job_id': self.active_job.pk}))
        self.assertEqual(res1.status_code, 404)

        # Attempt to view applicant detail
        res2 = self.client.get(reverse('applications:applicant_detail', kwargs={'pk': application.pk}))
        self.assertEqual(res2.status_code, 404)
