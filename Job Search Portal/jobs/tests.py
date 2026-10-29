from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from companies.models import Company
from .models import Job

User = get_user_model()


class JobSearchAndManagementTests(TestCase):
    """
    Test suite for Job posting, search, filtering, status toggling, and IDOR protection.
    """

    def setUp(self):
        self.client = Client()

        # Users
        self.employer_one = User.objects.create_user(
            username='recruiter_one',
            email='recruiter1@tech.com',
            password='Password@123',
            role=User.ROLE_EMPLOYER
        )
        self.employer_two = User.objects.create_user(
            username='recruiter_two',
            email='recruiter2@other.com',
            password='Password@123',
            role=User.ROLE_EMPLOYER
        )
        self.job_seeker = User.objects.create_user(
            username='candidate_alex',
            email='alex@example.com',
            password='Password@123',
            role=User.ROLE_JOB_SEEKER
        )

        # Company
        self.company = Company.objects.create(
            employer=self.employer_one,
            company_name='Alpha Tech Solutions',
            description='Innovating cloud technologies.',
            industry='technology',
            location='Bengaluru, India'
        )

        # Published Jobs
        self.job_django = Job.objects.create(
            company=self.company,
            created_by=self.employer_one,
            title='Senior Django Developer',
            category='software',
            job_type='full_time',
            experience_level='mid',
            location='Bengaluru, India',
            salary_min=800000.00,
            salary_max=1400000.00,
            status='PUBLISHED',
            description='Seeking a backend engineer with Django and MySQL expertise.',
            required_skills='Python, Django, MySQL, REST APIs, Redis',
            application_deadline=timezone.now().date() + timedelta(days=30)
        )

        self.job_react = Job.objects.create(
            company=self.company,
            created_by=self.employer_one,
            title='Frontend React Developer',
            category='software',
            job_type='remote',
            experience_level='fresher',
            location='Remote',
            salary_min=400000.00,
            salary_max=700000.00,
            status='PUBLISHED',
            description='Looking for creative UI developer with React and Bootstrap.',
            required_skills='JavaScript, React, HTML5, CSS3, Bootstrap',
            application_deadline=timezone.now().date() + timedelta(days=20)
        )

        # Draft Job (should NOT appear in public searches)
        self.draft_job = Job.objects.create(
            company=self.company,
            created_by=self.employer_one,
            title='Unpublished DevOps Engineer',
            category='devops_cloud',
            job_type='full_time',
            status='DRAFT',
            description='Draft position not ready for public viewing.',
            required_skills='AWS, Docker, Kubernetes'
        )

    def test_public_job_list_shows_only_published(self):
        """Public listing displays published jobs and hides draft/closed jobs."""
        response = self.client.get(reverse('jobs:job_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Senior Django Developer')
        self.assertContains(response, 'Frontend React Developer')
        self.assertNotContains(response, 'Unpublished DevOps Engineer')

    def test_job_search_by_keyword(self):
        """Search jobs by title or skill keyword."""
        response = self.client.get(reverse('jobs:job_list'), {'q': 'Django'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Senior Django Developer')
        self.assertNotContains(response, 'Frontend React Developer')

    def test_job_filter_by_type_and_location(self):
        """Filter jobs by job type (remote) and location."""
        response = self.client.get(reverse('jobs:job_list'), {
            'job_type': 'remote',
            'location': 'Remote'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Frontend React Developer')
        self.assertNotContains(response, 'Senior Django Developer')

    def test_job_filter_by_minimum_salary(self):
        """Filter jobs by minimum salary threshold."""
        response = self.client.get(reverse('jobs:job_list'), {'min_salary': '1000000'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Senior Django Developer')  # Max is 1,400,000
        self.assertNotContains(response, 'Frontend React Developer')  # Max is 700,000

    def test_job_detail_view_increments_views(self):
        """Visiting a job detail page increments view counter."""
        initial_views = self.job_django.views_count
        response = self.client.get(reverse('jobs:job_detail', kwargs={'pk': self.job_django.pk}))
        self.assertEqual(response.status_code, 200)
        self.job_django.refresh_from_db()
        self.assertEqual(self.job_django.views_count, initial_views + 1)

    def test_employer_can_create_job(self):
        """Employer can post a new job opening."""
        self.client.login(username='recruiter_one', password='Password@123')
        response = self.client.post(reverse('jobs:create_job'), {
            'title': 'AI & Machine Learning Engineer',
            'company': self.company.pk,
            'category': 'data_ai',
            'job_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Bengaluru, India',
            'salary_min': 1500000.00,
            'salary_max': 2500000.00,
            'status': 'PUBLISHED',
            'description': 'Building cutting-edge machine learning pipelines.',
            'required_skills': 'Python, PyTorch, TensorFlow, Scikit-learn',
            'application_deadline': (timezone.now().date() + timedelta(days=45)).isoformat()
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Job.objects.filter(title='AI & Machine Learning Engineer').exists())

    def test_job_creation_past_deadline_rejected(self):
        """Job creation with a past deadline fails form validation."""
        self.client.login(username='recruiter_one', password='Password@123')
        past_date = (timezone.now().date() - timedelta(days=5)).isoformat()
        response = self.client.post(reverse('jobs:create_job'), {
            'title': 'Past Deadline Job',
            'company': self.company.pk,
            'category': 'software',
            'job_type': 'full_time',
            'experience_level': 'entry',
            'location': 'Pune',
            'status': 'PUBLISHED',
            'description': 'Test description.',
            'required_skills': 'Python',
            'application_deadline': past_date
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'application_deadline', 'Application deadline cannot be in the past.')

    def test_job_creation_mismatched_salary_rejected(self):
        """Job creation where salary_max < salary_min fails form validation."""
        self.client.login(username='recruiter_one', password='Password@123')
        response = self.client.post(reverse('jobs:create_job'), {
            'title': 'Invalid Salary Job',
            'company': self.company.pk,
            'category': 'software',
            'job_type': 'full_time',
            'experience_level': 'entry',
            'location': 'Pune',
            'salary_min': 900000.00,
            'salary_max': 500000.00,  # Max < Min!
            'status': 'PUBLISHED',
            'description': 'Test description.',
            'required_skills': 'Python',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'salary_max', 'Maximum salary cannot be less than minimum salary.')

    def test_idor_protection_employer_cannot_edit_other_job(self):
        """Employer B cannot edit Employer A's job posting (returns 404)."""
        self.client.login(username='recruiter_two', password='Password@123')
        response = self.client.get(reverse('jobs:edit_job', kwargs={'pk': self.job_django.pk}))
        self.assertEqual(response.status_code, 404)

    def test_employer_toggle_job_status(self):
        """Employer can toggle active job to closed."""
        self.client.login(username='recruiter_one', password='Password@123')
        response = self.client.get(reverse('jobs:toggle_status', kwargs={'pk': self.job_django.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.job_django.refresh_from_db()
        self.assertEqual(self.job_django.status, 'CLOSED')

    def test_job_seeker_cannot_post_job(self):
        """Job seekers attempting to post a job are redirected."""
        self.client.login(username='candidate_alex', password='Password@123')
        response = self.client.get(reverse('jobs:create_job'), follow=True)
        self.assertRedirects(response, reverse('dashboard:seeker_dashboard'))
