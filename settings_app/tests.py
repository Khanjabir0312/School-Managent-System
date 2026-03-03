from django.test import TestCase, Client
from django.urls import reverse

from .models import Program, SchoolYear, Grade


class ProgramViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # create and login as superuser to access views
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_superuser('admin', 'a@b.com', 'pass')
        self.client.login(username='admin', password='pass')
        
    def test_program_list_empty(self):
        resp = self.client.get(reverse('settings_app:program_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'No programs defined yet')

    def test_program_create_and_list(self):
        # create program via form POST
        resp = self.client.post(reverse('settings_app:program_create'), {
            'name': 'Elementary',
            'code': 'ELE',
            'is_active': True,
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Program.objects.filter(code='ELE').exists())
        self.assertContains(resp, 'Elementary')
        # verify edit link present
        self.assertContains(resp, 'Edit')

    def test_program_edit(self):
        p = Program.objects.create(name='Middle', code='MID')
        url = reverse('settings_app:program_edit', args=[p.pk])
        resp = self.client.post(url, {
            'name': 'Middle School',
            'code': 'MID',
            'is_active': False,
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        p.refresh_from_db()
        self.assertEqual(p.name, 'Middle School')
        self.assertFalse(p.is_active)


class SchoolYearAndGradeTests(TestCase):
    def setUp(self):
        self.client = Client()
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_superuser('super', 's@x.com', 'pass')
        self.client.login(username='super', password='pass')

    def test_school_year_creation_and_activation(self):
        # create first year
        resp = self.client.post(reverse('settings_app:school_year_create'), {
            'name': '2024-2025',
            'start_date': '2024-09-01',
            'end_date': '2025-06-30',
            'is_active': True,
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(SchoolYear.objects.filter(name='2024-2025', is_active=True).exists())
        # create another active year should raise validation error
        resp2 = self.client.post(reverse('settings_app:school_year_create'), {
            'name': '2025-2026',
            'start_date': '2025-09-01',
            'end_date': '2026-06-30',
            'is_active': True,
        })
        self.assertContains(resp2, 'Only one school year can be active at a time', status_code=200)

    def test_grade_filters_by_program(self):
        prog = Program.objects.create(name='High', code='HIGH')
        prog2 = Program.objects.create(name='Low', code='LOW')
        Grade.objects.create(name='G1', code='G1', program=prog)
        Grade.objects.create(name='G2', code='G2', program=prog2)
        url = reverse('settings_app:grade_list')
        resp = self.client.get(url + f'?program={prog.id}')
        self.assertContains(resp, 'G1')
        self.assertNotContains(resp, 'G2')
