from datetime import date, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from website.models import ShopInfo, Service, Barber, Booking


class BookingSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.shop = ShopInfo.objects.create(
            name="Paradise Barber",
            description="Luxury grooming",
            phone_number="0911223344",
            location="Addis Ababa",
            opening_hours="09:00 AM - 08:00 PM",
            payment_instructions="CBE: 1000123456"
        )
        self.service = Service.objects.create(
            name="Haircut",
            description="Standard haircut",
            price=300.00,
            duration=30
        )
        self.barber = Barber.objects.create(
            name="Abebe",
            role="Senior Barber"
        )

        # Create dummy image for payment screenshot
        self.dummy_image = SimpleUploadedFile(
            name="test_receipt.gif",
            content=b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
            content_type="image/gif"
        )


        # Create staff user for dashboard
        self.staff_user = User.objects.create_user(
            username="barber_admin",
            email="admin@barber.com",
            password="password123",
            is_staff=True
        )


    def test_booking_creation_and_3day_limit(self):
        today = date.today()
        valid_date = today + timedelta(days=2)
        invalid_date = today + timedelta(days=5)

        # Valid booking
        booking = Booking.objects.create(
            customer_name="John Doe",
            phone_number="0911000111",
            service=self.service,
            barber=self.barber,
            appointment_date=valid_date,
            appointment_time="10:00:00",
            payment_screenshot=self.dummy_image,
            payment_status="pending",
            status="pending"
        )
        self.assertEqual(booking.payment_status, "pending")
        self.assertEqual(booking.status, "pending")

        # Test booking API endpoint slot logic
        response = self.client.get(f"/api/available-slots/?date={valid_date.strftime('%Y-%m-%d')}&service={self.service.id}&barber={self.barber.id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        slot_values = [s["value"] for s in data["slots"]]
        self.assertNotIn("10:00", slot_values) # 10:00 is booked, should not be available

        # Test invalid date API endpoint
        response = self.client.get(f"/api/available-slots/?date={invalid_date.strftime('%Y-%m-%d')}&service={self.service.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["slots"], [])

    def test_dashboard_access_control(self):
        # Unauthenticated user should be redirected to login
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 302)

        # Log in as staff
        self.client.login(username="barber_admin", password="password123")
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 200)

    def test_payment_verification_and_booking_confirmation(self):
        today = date.today()
        booking = Booking.objects.create(
            customer_name="Jane Smith",
            phone_number="0922334455",
            service=self.service,
            barber=self.barber,
            appointment_date=today + timedelta(days=1),
            appointment_time="14:00:00",
            payment_screenshot=self.dummy_image,
            payment_status="pending",
            status="pending"
        )

        self.client.login(username="barber_admin", password="password123")
        
        # Verify payment
        response = self.client.post(f"/dashboard/bookings/{booking.id}/", {"action": "verify_payment"})
        self.assertEqual(response.status_code, 302)

        booking.refresh_from_db()
        self.assertEqual(booking.payment_status, "verified")
        self.assertEqual(booking.status, "confirmed")

        # Mark completed
        response = self.client.post(f"/dashboard/bookings/{booking.id}/", {"action": "complete_booking"})
        booking.refresh_from_db()
        self.assertEqual(booking.status, "completed")
