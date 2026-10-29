from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Company

User = get_user_model()


class CompanyProfileTests(TestCase):
    """
    Test suite for company creation, editing, permissions, and directory listings.
    """

    def setUp(self):
        self.client = Client()
        self.employer_user = User.objects.create_user(
            username='recruiter_one',
            email='recruiter1@apex.com',
            password='Password@123',
            role=User.ROLE_EMPLOYER
        )
        self.other_employer = User.objects.create_user(
            username='recruiter_two',
            email='recruiter2@other.com',
            password='Password@123',
            role=User.ROLE_EMPLOYER
        )
        self.job_seeker_user = User.objects.create_user(
            username='applicant_bob',
            email='bob@example.com',
            password='Password@123',
            role=User.ROLE_JOB_SEEKER
        )
        self.company = Company.objects.create(
            employer=self.employer_user,
            company_name='Apex Technologies',
            description='Leading enterprise cloud solutions provider.',
            website='https://apex.example.com',
            industry='technology',
            company_size='51-200',
            location='Bengaluru, Karnataka'
        )

    def test_company_directory_public_access(self):
        """Unauthenticated visitors can browse the company directory."""
        response = self.client.get(reverse('companies:company_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Apex Technologies')

    def test_company_directory_filter(self):
        """Filter companies by keyword search."""
        response = self.client.get(reverse('companies:company_list'), {'q': 'Apex'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Apex Technologies')

        # Negative search
        response2 = self.client.get(reverse('companies:company_list'), {'q': 'NonExistentCorp'})
        self.assertEqual(response2.status_code, 200)
        self.assertContains(response2, 'No Companies Found')

    def test_company_detail_public_access(self):
        """Visitors can view company detail page."""
        response = self.client.get(reverse('companies:company_detail', kwargs={'pk': self.company.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Apex Technologies')
        self.assertContains(response, 'Leading enterprise cloud solutions provider.')

    def test_employer_can_create_company(self):
        """Employer can create a new company profile."""
        self.client.login(username='recruiter_two', password='Password@123')
        response = self.client.post(reverse('companies:create_company'), {
            'company_name': 'Quantum Robotics',
            'industry': 'technology',
            'company_size': '11-50',
            'location': 'Hyderabad, India',
            'website': 'https://quantum.example.com',
            'description': 'Building next-generation robotics software.',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Company.objects.filter(company_name='Quantum Robotics').exists())
        created_company = Company.objects.get(company_name='Quantum Robotics')
        self.assertEqual(created_company.employer, self.other_employer)

    def test_employer_can_edit_own_company(self):
        """Employer can edit their own company details."""
        self.client.login(username='recruiter_one', password='Password@123')
        response = self.client.post(reverse('companies:edit_company', kwargs={'pk': self.company.pk}), {
            'company_name': 'Apex Technologies Global',
            'industry': 'technology',
            'company_size': '201-500',
            'location': 'Bengaluru & Pune, India',
            'website': 'https://apexglobal.example.com',
            'description': 'Updated description.',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.company.refresh_from_db()
        self.assertEqual(self.company.company_name, 'Apex Technologies Global')
        self.assertEqual(self.company.company_size, '201-500')

    def test_idor_protection_employer_cannot_edit_other_company(self):
        """Employer B cannot edit Employer A's company (should 404)."""
        self.client.login(username='recruiter_two', password='Password@123')
        response = self.client.get(reverse('companies:edit_company', kwargs={'pk': self.company.pk}))
        self.assertEqual(response.status_code, 404)

    def test_job_seeker_cannot_create_company(self):
        """Job seeker trying to create a company is redirected to seeker dashboard."""
        self.client.login(username='applicant_bob', password='Password@123')
        response = self.client.get(reverse('companies:create_company'), follow=True)
        self.assertRedirects(response, reverse('dashboard:seeker_dashboard'))
