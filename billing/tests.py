from django.test import TestCase, override_settings
from django.utils import timezone
from datetime import date, timedelta

# use in-memory sqlite for testing to avoid needing postgres privileges
TEST_DB = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

from students.models import Student
from billing.models import FeeCategory, Discount, Invoice, InvoiceItem, Payment


@override_settings(DATABASES=TEST_DB)
class InvoiceModelTests(TestCase):
    def setUp(self):
        # create a student and fee category used in invoices
        self.student = Student.objects.create(
            student_id="S001",
            first_name="Test",
            last_name="Student",
        )
        self.fee = FeeCategory.objects.create(
            category_name="Tuition",
            default_amount=1000,
        )
        # create a discount that is currently valid
        self.discount = Discount.objects.create(
            discount_name="TenPercent",
            discount_type="percentage",
            discount_value=10,
            valid_from=date.today() - timedelta(days=1),
            valid_to=date.today() + timedelta(days=1),
        )

    def test_discount_amount_reset_when_invalid(self):
        """Invoice.calculate_totals should clear discount_amount when discount is invalid"""
        invoice = Invoice.objects.create(
            student=self.student,
            academic_year="2024-2025",
            due_date=date.today() + timedelta(days=30),
        )
        InvoiceItem.objects.create(
            invoice=invoice,
            fee_category=self.fee,
            description="Test item",
            quantity=1,
            unit_price=200,
        )
        invoice.discount = self.discount
        invoice.calculate_totals()
        # discount is valid -> discount_amount nonzero
        self.assertGreater(invoice.discount_amount, 0)
        # expire the discount and recalc
        self.discount.valid_to = date.today() - timedelta(days=1)
        self.discount.save()
        invoice.calculate_totals()
        self.assertEqual(invoice.discount_amount, 0)

    def test_invoice_status_updates_and_balance(self):
        invoice = Invoice.objects.create(
            student=self.student,
            academic_year="2024-2025",
            due_date=date.today() - timedelta(days=1),  # overdue already
        )
        InvoiceItem.objects.create(
            invoice=invoice,
            fee_category=self.fee,
            quantity=1,
            unit_price=100,
        )
        # after creation totals should be calculated
        invoice.calculate_totals()
        self.assertEqual(invoice.status, "overdue")
        # simulate payment
        payment = Payment.objects.create(
            invoice=invoice,
            amount=100,
        )
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, "paid")
        self.assertEqual(invoice.balance_amount, 0)


@override_settings(DATABASES=TEST_DB)
class PaymentModelTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            student_id="S002",
            first_name="Foo",
            last_name="Bar",
        )
        self.fee = FeeCategory.objects.create(
            category_name="Books",
            default_amount=500,
        )
        self.invoice = Invoice.objects.create(
            student=self.student,
            academic_year="2024-2025",
            due_date=date.today() + timedelta(days=10),
        )
        InvoiceItem.objects.create(
            invoice=self.invoice,
            fee_category=self.fee,
            quantity=2,
            unit_price=50,
        )
        self.invoice.calculate_totals()

    def test_payment_number_and_receipt_generated(self):
        p = Payment.objects.create(
            invoice=self.invoice,
            amount=50,
        )
        self.assertTrue(p.payment_number.startswith("PAY"))
        self.assertTrue(p.receipt_number.startswith("REC"))
        self.assertTrue(p.transaction_number.startswith("LIK"))

    def test_invoice_paid_amount_updates(self):
        p = Payment.objects.create(
            invoice=self.invoice,
            amount=25,
        )
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.paid_amount, 25)
        self.assertEqual(self.invoice.status, "partial")


class PageSmokeTests(TestCase):
    """Smoke tests that iterate through all registered URL patterns and ensure
    they don't result in 500 errors when accessed by a superuser.

    We substitute simple dummy values for path converters. 404 responses are
    allowed since no object may exist, but any 5xx error indicates a broken
    view.
    """

    @classmethod
    def setUpTestData(cls):
        # create a superuser to bypass permissions
        from django.contrib.auth import get_user_model
        User = get_user_model()
        cls.admin = User.objects.create_superuser(username='smoketest', password='pass')

    def setUp(self):
        self.client.login(username='smoketest', password='pass')

    def _collect_routes(self, patterns):
        from django.urls.resolvers import URLResolver, URLPattern
        routes = []
        for entry in patterns:
            if isinstance(entry, URLResolver):
                routes += self._collect_routes(entry.url_patterns)
            elif isinstance(entry, URLPattern):
                # pattern may be RegexPattern or RoutePattern
                # str(pattern) should give the raw regex or route
                route = str(entry.pattern)
                # strip anchors
                route = route.lstrip('^').rstrip('$')
                routes.append(route)
        return routes

    def _build_url(self, route):
        # replace path converters with dummy values
        import re
        url = route
        url = re.sub(r'<int:[^>]+>', '1', url)
        url = re.sub(r'<str:[^>]+>', 'test', url)
        url = re.sub(r'<slug:[^>]+>', 'test-slug', url)
        url = re.sub(r'<uuid:[^>]+>', '00000000-0000-0000-0000-000000000000', url)
        # generic catch-all for other converters
        url = re.sub(r'<[^>]+>', '1', url)
        if not url.startswith('/'):
            url = '/' + url
        # ensure trailing slash
        if not url.endswith('/'):
            url += '/'
        return url

    def test_all_pages_load_without_server_error(self):
        from django.urls import get_resolver
        resolver = get_resolver()
        routes = self._collect_routes(resolver.url_patterns)
        errors = []
        for route in routes:
            # skip admin and static/media and debug toolbar if present
            if route.startswith('admin') or route.startswith('static') or route.startswith('media'):
                continue
            url = self._build_url(route)
            resp = self.client.get(url)
            if resp.status_code >= 500:
                errors.append((url, resp.status_code))
        if errors:
            self.fail(f"Endpoints returned server error: {errors}")

