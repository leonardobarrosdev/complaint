import json, ipdb
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.test import TestCase, Client
from django.urls import reverse
from .models import Complaint


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


class SlistTest(TestCase):
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
        response = self.client.get('/slist/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('result', response.context)
        # self.assertEqual(response.context['result'], result)


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
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ComplaintMS/AllComplaints.html')

        complaint = Complaint.objects.all().exclude(status='1')
        self.assertEqual(len(response.context['c']), complaint.count())

        # Test filtering by type_of_complaint
        response = self.client.get(reverse('all_complaints') + '?drop=Type')
        self.assertEqual(len(response.context['c']), complaint.filter(type_of_complaint__icontains='Type').count())

        # Test searching by type_of_complaint, description, and subject
        response = self.client.get(reverse('all_complaints') + '?search=keyword')
        self.assertEqual(len(response.context['c']), complaint.filter(
            Q(type_of_complaint__icontains='keyword') | Q(description__icontains='keyword') | Q(
                subject__icontains='keyword')).count())

        # Test POST request
        complaint_to_resolve = complaint.first()
        response_post = self.client.post(
            reverse('all_complaints'),
            {'cid2': complaint_to_resolve.id, 'uid': complaint_to_resolve.user_id, 'status': 3}
        )
        self.assertEqual(response_post.status_code, 302)  # Redirect after successful post
        self.assertEqual(complaint_to_resolve.status, 3)  # Assuming status is updated to '1' on successful post