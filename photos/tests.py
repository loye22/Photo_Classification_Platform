from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from photos.models import User, Photo, Submission

class AdminPanelTests(TestCase):
    def setUp(self):
        # Create a regular user
        self.regular_user = User.objects.create_user(
            username='user@test.com',
            email='user@test.com',
            password='password123',
            is_admin=False
        )

        # Create an admin user
        self.admin_user = User.objects.create_user(
            username='admin@test.com',
            email='admin@test.com',
            password='password123',
            is_admin=True
        )

        # Create sample photos
        self.photo1 = Photo.objects.create(
            storage_url='/media/photos/test1.png',
            file_name='test1.png',
            mime_type='image/png',
            size_bytes=1024
        )
        self.photo2 = Photo.objects.create(
            storage_url='/media/photos/test2.png',
            file_name='test2.png',
            mime_type='image/png',
            size_bytes=2048
        )

        # Create sample submissions
        self.submission1 = Submission.objects.create(
            user=self.regular_user,
            photo=self.photo1,
            name='Alice Smith',
            age=25,
            gender='female',
            place_of_living='New York',
            country_of_origin='USA',
            description='Test Alice photo',
            status='pending'
        )

        self.submission2 = Submission.objects.create(
            user=self.regular_user,
            photo=self.photo2,
            name='Bob Jones',
            age=40,
            gender='male',
            place_of_living='London',
            country_of_origin='UK',
            description='Test Bob photo',
            status='processed'
        )

        self.admin_panel_url = reverse('admin_panel')

    def test_anonymous_user_cannot_access_admin_panel(self):
        """Anonymous users should be redirected to the login page."""
        response = self.client.get(self.admin_panel_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn(reverse('login'), response.url)

    def test_regular_user_cannot_access_admin_panel(self):
        """Regular users should get a 403 Forbidden permission error."""
        self.client.login(email='user@test.com', password='password123')
        response = self.client.get(self.admin_panel_url)
        self.assertEqual(response.status_code, 403)

    def test_admin_user_can_access_admin_panel(self):
        """Admin users should be able to access the admin panel page successfully."""
        self.client.login(email='admin@test.com', password='password123')
        response = self.client.get(self.admin_panel_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'photos/admin_panel.html')

    def test_admin_can_search_submissions(self):
        """Admin should be able to search submissions by keyword."""
        self.client.login(email='admin@test.com', password='password123')
        
        # Search matching 'Alice'
        response = self.client.get(self.admin_panel_url, {'search': 'Alice'})
        self.assertEqual(response.status_code, 200)
        submissions = response.context['submissions']
        self.assertEqual(submissions.count(), 1)
        self.assertEqual(submissions.first(), self.submission1)

        # Search matching 'London'
        response = self.client.get(self.admin_panel_url, {'search': 'London'})
        self.assertEqual(response.status_code, 200)
        submissions = response.context['submissions']
        self.assertEqual(submissions.count(), 1)
        self.assertEqual(submissions.first(), self.submission2)

    def test_admin_can_filter_submissions(self):
        """Admin should be able to filter submissions using criteria."""
        self.client.login(email='admin@test.com', password='password123')

        # Filter by gender
        response = self.client.get(self.admin_panel_url, {'gender': 'male'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['submissions'].count(), 1)
        self.assertEqual(response.context['submissions'].first(), self.submission2)

        # Filter by status
        response = self.client.get(self.admin_panel_url, {'status': 'pending'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['submissions'].count(), 1)
        self.assertEqual(response.context['submissions'].first(), self.submission1)

        # Filter by country
        response = self.client.get(self.admin_panel_url, {'country': 'USA'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['submissions'].count(), 1)
        self.assertEqual(response.context['submissions'].first(), self.submission1)

        # Filter by age range
        response = self.client.get(self.admin_panel_url, {'min_age': 30, 'max_age': 50})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['submissions'].count(), 1)
        self.assertEqual(response.context['submissions'].first(), self.submission2)

    def test_admin_can_update_submission_status(self):
        """Admin should be able to update status of a submission."""
        self.client.login(email='admin@test.com', password='password123')
        
        # Verify initial status is pending
        self.assertEqual(self.submission1.status, 'pending')

        # POST status update
        response = self.client.post(self.admin_panel_url, {
            'action': 'update_status',
            'submission_id': str(self.submission1.id),
            'status': 'processed'
        })
        
        # Should redirect to admin panel
        self.assertRedirects(response, self.admin_panel_url)

        # Reload submission from DB and check status
        self.submission1.refresh_from_db()
        self.assertEqual(self.submission1.status, 'processed')
