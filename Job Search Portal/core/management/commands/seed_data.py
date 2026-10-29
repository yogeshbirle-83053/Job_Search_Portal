from datetime import timedelta
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone
from django.contrib.auth import get_user_model
from companies.models import Company
from jobs.models import Job
from applications.models import JobApplication, SavedJob
from accounts.models import JobSeekerProfile

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds realistic demonstration sample data (employers, companies, jobs, seekers, applications)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Job Search Portal demonstration data..."))

        # 1. Superuser / Admin
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                'email': 'admin@jobportal.com',
                'role': User.ROLE_ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password("AdminPassword@123")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created Superuser: admin / AdminPassword@123"))

        # 2. Sample Employers
        emp1, _ = User.objects.get_or_create(
            username="google_recruiter",
            defaults={'email': 'recruiting@google.example.com', 'role': User.ROLE_EMPLOYER}
        )
        emp1.set_password("Password@123")
        emp1.save()

        emp2, _ = User.objects.get_or_create(
            username="microsoft_recruiter",
            defaults={'email': 'careers@microsoft.example.com', 'role': User.ROLE_EMPLOYER}
        )
        emp2.set_password("Password@123")
        emp2.save()

        emp3, _ = User.objects.get_or_create(
            username="infosys_recruiter",
            defaults={'email': 'talent@infosys.example.com', 'role': User.ROLE_EMPLOYER}
        )
        emp3.set_password("Password@123")
        emp3.save()

        # 3. Sample Companies
        comp1, _ = Company.objects.get_or_create(
            company_name="Google India",
            defaults={
                'employer': emp1,
                'industry': 'technology',
                'company_size': '500+',
                'location': 'Bengaluru, Karnataka, India',
                'website': 'https://about.google',
                'description': 'Our mission is to organize the world’s information and make it universally accessible and useful. We build products that help billions of people navigate, connect, and learn.'
            }
        )

        comp2, _ = Company.objects.get_or_create(
            company_name="Microsoft India",
            defaults={
                'employer': emp2,
                'industry': 'technology',
                'company_size': '500+',
                'location': 'Hyderabad, Telangana, India',
                'website': 'https://www.microsoft.com',
                'description': 'Microsoft enables digital transformation for the era of an intelligent cloud and an intelligent edge. Our mission is to empower every person and every organization on the planet to achieve more.'
            }
        )

        comp3, _ = Company.objects.get_or_create(
            company_name="Infosys Limited",
            defaults={
                'employer': emp3,
                'industry': 'consulting',
                'company_size': '500+',
                'location': 'Pune, Maharashtra, India',
                'website': 'https://www.infosys.com',
                'description': 'A global leader in next-generation digital services and consulting. We enable clients in more than 56 countries to navigate their digital transformation with cloud and AI.'
            }
        )

        self.stdout.write(self.style.SUCCESS("Created Companies: Google India, Microsoft India, Infosys Limited"))

        # 4. Sample Jobs
        today = timezone.now().date()
        job1, _ = Job.objects.get_or_create(
            title="Senior Full Stack Django Developer",
            company=comp1,
            defaults={
                'created_by': emp1,
                'category': 'software',
                'job_type': 'full_time',
                'experience_level': 'mid',
                'location': 'Bengaluru, Karnataka',
                'salary_min': 1000000.00,
                'salary_max': 1600000.00,
                'status': 'PUBLISHED',
                'application_deadline': today + timedelta(days=45),
                'description': 'We are looking for an experienced Full Stack Python & Django Developer to build scalable enterprise web applications and robust RESTful APIs.',
                'responsibilities': '- Architect and implement high-performance web applications using Django & MySQL.\n- Build responsive, accessible frontends using Bootstrap 5 and modern JavaScript.\n- Optimize complex database queries and implement Redis caching strategies.\n- Collaborate with product managers and security specialists.',
                'required_skills': 'Python, Django, MySQL, REST APIs, Bootstrap 5, JavaScript, Git, Docker'
            }
        )

        job2, _ = Job.objects.get_or_create(
            title="Frontend React & UI/UX Developer",
            company=comp1,
            defaults={
                'created_by': emp1,
                'category': 'software',
                'job_type': 'remote',
                'experience_level': 'entry',
                'location': 'Remote (India)',
                'salary_min': 600000.00,
                'salary_max': 1000000.00,
                'status': 'PUBLISHED',
                'application_deadline': today + timedelta(days=30),
                'description': 'Join our frontend team building interactive dashboards, accessible user interfaces, and mobile-friendly experiences for enterprise clients.',
                'responsibilities': '- Implement reusable UI components in React and Vanilla JavaScript.\n- Integrate backend JSON APIs.\n- Ensure cross-browser compatibility and responsive design standards.',
                'required_skills': 'JavaScript, React, HTML5, CSS3, Bootstrap 5, REST APIs'
            }
        )

        job3, _ = Job.objects.get_or_create(
            title="Cloud DevOps & Site Reliability Engineer",
            company=comp2,
            defaults={
                'created_by': emp2,
                'category': 'devops_cloud',
                'job_type': 'full_time',
                'experience_level': 'senior',
                'location': 'Hyderabad, Telangana',
                'salary_min': 1400000.00,
                'salary_max': 2200000.00,
                'status': 'PUBLISHED',
                'application_deadline': today + timedelta(days=60),
                'description': 'Drive automation, infrastructure-as-code, and high-availability operations across our global cloud deployment footprint.',
                'responsibilities': '- Manage Kubernetes clusters and CI/CD pipelines.\n- Monitor system performance, uptime, and database clustering.\n- Implement security compliance and automated recovery drills.',
                'required_skills': 'Docker, Kubernetes, AWS, Azure, Linux, Python, CI/CD, Terraform'
            }
        )

        job4, _ = Job.objects.get_or_create(
            title="Machine Learning & AI Research Engineer",
            company=comp2,
            defaults={
                'created_by': emp2,
                'category': 'data_ai',
                'job_type': 'full_time',
                'experience_level': 'senior',
                'location': 'Bengaluru, Karnataka',
                'salary_min': 1600000.00,
                'salary_max': 2600000.00,
                'status': 'PUBLISHED',
                'application_deadline': today + timedelta(days=40),
                'description': 'Develop, train, and deploy advanced machine learning models and NLP pipelines to empower enterprise analytics products.',
                'responsibilities': '- Design and train deep learning models using PyTorch.\n- Deploy low-latency inference microservices.\n- Clean and preprocess terabyte-scale datasets.',
                'required_skills': 'Python, PyTorch, TensorFlow, NLP, Scikit-learn, SQL, Docker'
            }
        )

        job5, _ = Job.objects.get_or_create(
            title="UI/UX Product Designer",
            company=comp3,
            defaults={
                'created_by': emp3,
                'category': 'design',
                'job_type': 'contract',
                'experience_level': 'mid',
                'location': 'Remote / Pune',
                'salary_min': 700000.00,
                'salary_max': 1200000.00,
                'status': 'PUBLISHED',
                'application_deadline': today + timedelta(days=25),
                'description': 'Lead user experience discovery, design intuitive wireframes, and craft high-fidelity mockups for enterprise web applications.',
                'responsibilities': '- Conduct user interviews and usability testing.\n- Create user journeys, personas, wireframes, and prototypes in Figma.\n- Partner with developers to inspect UI implementation fidelity.',
                'required_skills': 'Figma, Wireframing, Prototyping, User Research, Design Systems'
            }
        )

        job6, _ = Job.objects.get_or_create(
            title="Graduate Software Engineering Intern",
            company=comp3,
            defaults={
                'created_by': emp3,
                'category': 'software',
                'job_type': 'internship',
                'experience_level': 'fresher',
                'location': 'Pune, Maharashtra',
                'salary_min': 360000.00,
                'salary_max': 480000.00,
                'status': 'PUBLISHED',
                'application_deadline': today + timedelta(days=20),
                'description': 'Ideal internship for final-year students and fresh graduates looking to kickstart their software development career with hands-on mentoring.',
                'responsibilities': '- Learn and contribute to production web features under senior engineer guidance.\n- Write clean unit tests and participate in code reviews.\n- Document API endpoints and technical designs.',
                'required_skills': 'Python, SQL, HTML, CSS, JavaScript, Git'
            }
        )

        self.stdout.write(self.style.SUCCESS("Created 6 Published Jobs across Software, DevOps, AI, Design, and Internships."))

        # 5. Sample Job Seekers
        sample_pdf_bytes = b"%PDF-1.4\n% Sample PDF Resume Content for Demonstration\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"

        seeker1, _ = User.objects.get_or_create(
            username="john_seeker",
            defaults={'email': 'john.seeker@example.com', 'role': User.ROLE_JOB_SEEKER}
        )
        seeker1.set_password("Password@123")
        seeker1.save()

        p1, _ = JobSeekerProfile.objects.get_or_create(user=seeker1)
        p1.full_name = "Johnathan Doe"
        p1.phone = "+91 9876543210"
        p1.location = "Bengaluru, Karnataka, India"
        p1.professional_summary = "Enthusiastic Full Stack Python & Django developer with 2 years of experience building secure web applications, database schemas, and REST APIs."
        p1.skills = "Python, Django, MySQL, REST APIs, HTML5, CSS3, Bootstrap 5, JavaScript, Git"
        p1.education = "B.Tech in Computer Science, Visvesvaraya Technological University (2020 - 2024) - CGPA 8.7"
        p1.experience = "Junior Software Developer Intern at CloudNine Technologies (6 Months):\n- Developed customer-facing Django endpoints and optimized MySQL queries.\n- Automated unit tests achieving 90% code coverage."
        p1.resume.save("john_doe_resume.pdf", ContentFile(sample_pdf_bytes), save=False)
        p1.save()

        seeker2, _ = User.objects.get_or_create(
            username="priya_sharma",
            defaults={'email': 'priya.sharma@example.com', 'role': User.ROLE_JOB_SEEKER}
        )
        seeker2.set_password("Password@123")
        seeker2.save()

        p2, _ = JobSeekerProfile.objects.get_or_create(user=seeker2)
        p2.full_name = "Priya Sharma"
        p2.phone = "+91 9123456789"
        p2.location = "Hyderabad, Telangana, India"
        p2.professional_summary = "Frontend engineer passionate about designing clean, accessible, and high-performance user interfaces in React and Bootstrap."
        p2.skills = "JavaScript, React, HTML5, CSS3, Bootstrap 5, Figma, Git"
        p2.education = "B.E. in Information Technology, Osmania University (2020 - 2024)"
        p2.experience = "Frontend Engineering Intern at WebCraft (4 Months):\n- Built interactive UI components with responsive mobile layouts.\n- Reduced asset bundle sizes by 25%."
        p2.resume.save("priya_sharma_resume.pdf", ContentFile(sample_pdf_bytes), save=False)
        p2.save()

        self.stdout.write(self.style.SUCCESS("Created Job Seekers: john_seeker, priya_sharma with complete profiles & PDF resumes."))

        # 6. Sample Applications
        app1, created = JobApplication.objects.get_or_create(
            job=job1,
            applicant=seeker1,
            defaults={
                'status': JobApplication.STATUS_SHORTLISTED,
                'cover_letter': 'I have built multiple production Django applications and optimized MySQL queries for low latency. My experience directly matches your Senior Full Stack opening.'
            }
        )
        if created:
            app1.resume.save("john_app1_resume.pdf", ContentFile(sample_pdf_bytes), save=True)

        app2, created = JobApplication.objects.get_or_create(
            job=job2,
            applicant=seeker2,
            defaults={
                'status': JobApplication.STATUS_UNDER_REVIEW,
                'cover_letter': 'Excited about building clean web experiences at Google India. I am proficient in modern JavaScript and Bootstrap 5.'
            }
        )
        if created:
            app2.resume.save("priya_app2_resume.pdf", ContentFile(sample_pdf_bytes), save=True)

        app3, created = JobApplication.objects.get_or_create(
            job=job3,
            applicant=seeker1,
            defaults={
                'status': JobApplication.STATUS_APPLIED,
                'cover_letter': 'Eager to apply my Python automation and Linux infrastructure skills to your Cloud DevOps opening.'
            }
        )
        if created:
            app3.resume.save("john_app3_resume.pdf", ContentFile(sample_pdf_bytes), save=True)

        # 7. Sample Saved Jobs
        SavedJob.objects.get_or_create(user=seeker1, job=job4)
        SavedJob.objects.get_or_create(user=seeker2, job=job1)

        self.stdout.write(self.style.SUCCESS("=" * 65))
        self.stdout.write(self.style.SUCCESS("DEMO DATA SEEDED SUCCESSFULLY!"))
        self.stdout.write(self.style.SUCCESS("=" * 65))
        self.stdout.write("Credentials Summary:")
        self.stdout.write("  Admin / Superuser : admin / AdminPassword@123")
        self.stdout.write("  Employer 1 (Google): google_recruiter / Password@123")
        self.stdout.write("  Employer 2 (MSFT)  : microsoft_recruiter / Password@123")
        self.stdout.write("  Employer 3 (Infosys): infosys_recruiter / Password@123")
        self.stdout.write("  Job Seeker 1      : john_seeker / Password@123")
        self.stdout.write("  Job Seeker 2      : priya_sharma / Password@123")
        self.stdout.write("=" * 65)
