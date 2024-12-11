import ipdb
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.test import TestCase, Client
from django.urls import reverse
from .models import Complaint
from .views import complaints


class CounterTest(TestCase):
    fixtures = [
        "ComplaintMS/fixtures/user_fixture.json",
        "ComplaintMS/fixtures/complaint_fixture.json"
    ]

    def setUp(self):
        self.client = Client()
        self.unsolved = Complaint.objects.all().exclude(status='1').count()
        self.solved = Complaint.objects.all().exclude(Q(status='3') | Q(status='2')).count()

    def test_counter_success(self):
        response = self.client.get(reverse('counter'))
        self.assertEquals(response.status_code, 200)
        self.assertIn('unsolved', response.context)
        self.assertIn('solved', response.context)
        self.assertEqual(response.context['unsolved'], self.unsolved)
        self.assertEqual(response.context['solved'], self.solved)


class RegisterTest(TestCase):
    fixtures = [
        "ComplaintMS/fixtures/user_fixture.json",
        "ComplaintMS/fixtures/profile_fixture.json"
    ]

    def setUp(self):
        self.client = Client()
        self.data = {
            **{'username': 'J0hnDo3', 'first_name': 'John', 'last_name': 'Doe',
                'email': 'jd3@company.com', 'password1': 'secureP4ssword123', 'password2': 'secureP4ssword123'},
            **{'company': 2, 'phone': '', 'type_user': 'student', 'branch': 2}
        }

    def test_register_success(self):
        response = self.client.post(reverse('register'), data=self.data)
        self.assertRedirects(response, '/login/', 302)


class DashboardTest(TestCase):
    fixtures = [
        "ComplaintMS/fixtures/user_fixture.json",
        "ComplaintMS/fixtures/profile_fixture.json"
    ]

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.get(id=1)
        self.client.force_login(self.user)
        self.data = {
            **{'company': 2, 'phone': '86996003245', 'branch': 2},
            **{'company': 2, 'phone': '86996003245', 'branch': 2}
        }

    def test_update_success(self):
        response = self.client.post(reverse('dashboard'), data=self.data)
        self.assertEqual(response.status_code, 200)


class ComplaintsTest(TestCase):
    fixtures = [
        "ComplaintMS/fixtures/user_fixture.json",
        "ComplaintMS/fixtures/profile_fixture.json",
        "ComplaintMS/fixtures/complaint_fixture.json"
    ]

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.get(id=1)
        self.client.force_login(self.user)
        self.data = {'subject': 'Technology', 'type_of_complaint': 'Academic', 'description': 'Use from classroom'}

    def test_create_success(self):
        response = self.client.post(reverse('complaints'), data=self.data)
        self.assertEqual(response.status_code, 200)


class SolvedsTest(TestCase):
    fixtures = [
        "ComplaintMS/fixtures/user_fixture.json",
        "ComplaintMS/fixtures/profile_fixture.json",
        "ComplaintMS/fixtures/complaint_fixture.json"
    ]

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.get(id=2)
        self.client.force_login(self.user)

    def test_list_success(self):
        result = Complaint.objects.filter(user=self.user).exclude(Q(status='3') | Q(status='2'))
        response = self.client.get(reverse('solveds'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('result', response.context)


class AllComplaintTest(TestCase):
    fixtures = [
        "ComplaintMS/fixtures/user_fixture.json",
        "ComplaintMS/fixtures/profile_fixture.json",
        "ComplaintMS/fixtures/complaint_fixture.json"
    ]

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.get(id=2)
        self.client.force_login(self.user)

    def test_get_complaints(self):
        response = self.client.get(reverse('all_complaints'))
        complaint = Complaint.objects.all().exclude(status='1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ComplaintMS/AllComplaints.html')
        self.assertEqual(len(response.context['c']), complaint.count())

    def test_filtering_by_type_of_complaint(self):
        complaint = Complaint.objects.all().exclude(status='1')
        response = self.client.get(reverse('all_complaints') + '?drop=Type')
        self.assertEqual(len(response.context['c']), complaint.filter(type_of_complaint__icontains='Type').count())

    def test_filter_by_fields(self):
        """Test searching by type_of_complaint, description, and subject"""
        complaint = Complaint.objects.all().exclude(status='1')
        response = self.client.get(reverse('all_complaints') + '?search=keyword')
        self.assertEqual(len(response.context['c']), complaint.filter(
            Q(type_of_complaint__icontains='keyword') |
            Q(description__icontains='keyword') |
            Q(subject__icontains='keyword')).count()
        )

    def test_post_complaint(self):
        complaint = Complaint.objects.all().exclude(status='1')
        complaint_to_resolve = complaint.first()
        response_post = self.client.post(
            reverse('all_complaints'),
            {'cid2': complaint_to_resolve.id, 'uid': complaint_to_resolve.user_id, 'status': 3}
        )
        self.assertEqual(response_post.status_code, 302)
        self.assertEqual(complaint_to_resolve.status, 3)


class SolvedComplaintTest(TestCase):
    fixtures = [
        "ComplaintMS/fixtures/user_fixture.json",
        "ComplaintMS/fixtures/complaint_fixture.json"
    ]

    def setUp(self):
        self.user = get_user_model().objects.get(id=4)
        self.complaints = [
            Complaint.objects.get(id=9),
            Complaint.objects.get(id=10)
        ]
        self.client = Client()
        self.client.force_login(self.user)

    def test_view_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('solved'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith(reverse('signin')))

    def test_view_access_with_login(self):
        response = self.client.get(reverse('solved'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ComplaintMS/solved.html')

    def test_complaint_filtering_by_drop(self):
        response = self.client.get(reverse('solved') + '?drop=Technical')
        filtered_complaints = response.context['c']
        self.assertEqual(filtered_complaints.count(), 1)
        self.assertEqual(filtered_complaints[0].type_of_complaint, 'Technical')

    def test_complaint_search(self):
        response = self.client.get(reverse('solved') + '?search=Technical')
        response1 = self.client.get(reverse('solved') + '?search=Network')
        response2 = self.client.get(reverse('solved') + '?search=Internet')
        self.assertEqual(response.context['c'].count(), 1)
        self.assertEqual(response1.context['c'].count(), 1)
        self.assertEqual(response2.context['c'].count(), 1)

    def test_update_complaint_status(self):
        complaint = self.complaints[0]
        update_data = {
            'cid2': complaint.id,
            'status': 1,
            'notes': 'Complaint resolved successfully'
        }
        response = self.client.post(reverse('solved'), update_data)
        self.assertRedirects(response, reverse('solved'))
        # Refresh complaint from database
        updated_complaint = Complaint.objects.get(id=complaint.id)
        self.assertEqual(updated_complaint.status, 1)

    def test_invalid_complaint_update(self):
        invalid_data = {'cid2': 9999, 'status': '2'}
        with self.assertRaises(Complaint.DoesNotExist):
            raise self.client.post(reverse('solved'), invalid_data)

    def test_complaints_exclude_resolved_and_closed(self):
        response = self.client.get(reverse('solved'))
        complaints = response.context['c']
        self.assertEqual(complaints.count(), 2)
        for complaint in complaints:
            self.assertNotIn(complaint.status, [2, 3])