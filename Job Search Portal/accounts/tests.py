from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountsAuthenticationTests(TestCase):
    """
    Test suite for user registration, authentication, and role-based permissions.
    """

    def setUp(self):
        self.client = Client()
        self.job_seeker_user = User.objects.create_user(
            username='seeker_jane',
            email='jane@example.com',
            password='Password@123',
            role=User.ROLE_JOB_SEEKER
        )
        self.employer_user = User.objects.create_user(
            username='employer_techcorp',
            email='hr@techcorp.com',
            password='Password@123',
            role=User.ROLE_EMPLOYER
        )

    def test_custom_user_roles(self):
        """Verify role helper methods and model properties."""
        self.assertTrue(self.job_seeker_user.is_job_seeker)
        self.assertFalse(self.job_seeker_user.is_employer)
        self.assertTrue(self.employer_user.is_employer)
        self.assertFalse(self.employer_user.is_job_seeker)

    def test_user_registration_job_seeker(self):
        """Test registering a new Job Seeker successfully."""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newseeker',
            'email': 'newseeker@example.com',
            'role': User.ROLE_JOB_SEEKER,
            'password': 'SecurePassword@123',
            'confirm_password': 'SecurePassword@123',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='newseeker').exists())
        created_user = User.objects.get(username='newseeker')
        self.assertEqual(created_user.role, User.ROLE_JOB_SEEKER)

    def test_user_registration_employer(self):
        """Test registering a new Employer successfully."""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newrecruiter',
            'email': 'recruiter@company.com',
            'role': User.ROLE_EMPLOYER,
            'password': 'SecurePassword@123',
            'confirm_password': 'SecurePassword@123',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='newrecruiter').exists())
        created_user = User.objects.get(username='newrecruiter')
        self.assertEqual(created_user.role, User.ROLE_EMPLOYER)

    def test_registration_duplicate_email_fails(self):
        """Test registration fails when an email is already registered."""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'anotheruser',
            'email': 'jane@example.com',  # Already belongs to seeker_jane
            'role': User.ROLE_JOB_SEEKER,
            'password': 'SecurePassword@123',
            'confirm_password': 'SecurePassword@123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'email', 'An account with this email address already exists.')

    def test_registration_mismatched_passwords_fails(self):
        """Test registration fails when password and confirm_password do not match."""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'mismatchuser',
            'email': 'mismatch@example.com',
            'role': User.ROLE_JOB_SEEKER,
            'password': 'Password1!',
            'confirm_password': 'Password2!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'confirm_password', 'Passwords do not match. Please re-enter them carefully.')

    def test_login_success_and_logout(self):
        """Test logging in with valid credentials and then logging out."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'seeker_jane',
            'password': 'Password@123',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        # Check user is authenticated in session
        self.assertTrue('_auth_user_id' in self.client.session)

        # Now test logout
        logout_response = self.client.get(reverse('accounts:logout'), follow=True)
        self.assertEqual(logout_response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_login_invalid_credentials(self):
        """Test logging in with wrong password fails."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'seeker_jane',
            'password': 'WrongPassword123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_role_based_access_seeker_to_employer_dashboard(self):
        """Job seeker trying to access employer dashboard gets redirected."""
        self.client.login(username='seeker_jane', password='Password@123')
        response = self.client.get(reverse('dashboard:employer_dashboard'), follow=True)
        # Should be redirected to seeker dashboard
        self.assertRedirects(response, reverse('dashboard:seeker_dashboard'))

    def test_role_based_access_employer_to_seeker_dashboard(self):
        """Employer trying to access seeker dashboard gets redirected."""
        self.client.login(username='employer_techcorp', password='Password@123')
        response = self.client.get(reverse('dashboard:seeker_dashboard'), follow=True)
        # Should be redirected to employer dashboard
        self.assertRedirects(response, reverse('dashboard:employer_dashboard'))

    def test_seeker_profile_auto_created(self):
        """Registering a job seeker automatically creates their JobSeekerProfile."""
        self.assertTrue(hasattr(self.job_seeker_user, 'seeker_profile'))
        self.assertEqual(self.job_seeker_user.seeker_profile.full_name, 'seeker_jane')

    def test_seeker_can_update_profile(self):
        """Job seeker can update their bio, skills, education, and location."""
        self.client.login(username='seeker_jane', password='Password@123')
        response = self.client.post(reverse('accounts:edit_profile'), {
            'full_name': 'Jane Doe',
            'phone': '+91 9999888877',
            'location': 'Bengaluru, India',
            'professional_summary': 'Full stack Django developer with 2 years of experience.',
            'skills': 'Python, Django, MySQL, Bootstrap 5, JavaScript',
            'education': 'B.Tech Computer Science, 2023',
            'experience': 'Intern at SoftTech (6 months)',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        profile = self.job_seeker_user.seeker_profile
        profile.refresh_from_db()
        self.assertEqual(profile.full_name, 'Jane Doe')
        self.assertIn('Django', profile.get_skills_list())

    def test_valid_pdf_resume_upload(self):
        """Uploading a valid PDF resume succeeds."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.login(username='seeker_jane', password='Password@123')

        pdf_content = b"%PDF-1.4 sample pdf content for testing resume upload"
        dummy_pdf = SimpleUploadedFile("my_resume.pdf", pdf_content, content_type="application/pdf")

        response = self.client.post(reverse('accounts:upload_resume'), {
            'resume': dummy_pdf,
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.job_seeker_user.seeker_profile.refresh_from_db()
        self.assertTrue(self.job_seeker_user.seeker_profile.has_resume)

    def test_invalid_resume_rejected(self):
        """Uploading a non-PDF file (.txt or invalid header) fails validation."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.login(username='seeker_jane', password='Password@123')

        txt_content = b"This is plain text, not a PDF."
        dummy_txt = SimpleUploadedFile("resume.txt", txt_content, content_type="text/plain")

        response = self.client.post(reverse('accounts:upload_resume'), {
            'resume': dummy_txt,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'resume',
            'Unsupported file format. Please upload a PDF file (.pdf).'
        )
