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

    def test_ethiopian_date_and_time_formatting(self):
        from website.utils import format_date_by_lang, format_time_by_lang
        from datetime import date, time

        # Test Date: August 10, 2026 -> Ethiopian 2018-12-04 (ሰኞ፣ ነሐሴ 4 2018)
        dt = date(2026, 8, 10)
        eth_date_str = format_date_by_lang(dt, lang="am")
        en_date_str = format_date_by_lang(dt, lang="en")

        self.assertIn("ነሐሴ 4 2018", eth_date_str)
        self.assertEqual(en_date_str, "Monday, August 10, 2026")

        # Test Time: 10:30 AM -> 4:30 ጧት
        t1 = time(10, 30)
        self.assertEqual(format_time_by_lang(t1, lang="am"), "4:30 ጧት")
        self.assertEqual(format_time_by_lang(t1, lang="en"), "10:30 AM")

        # Test Time: 2:15 PM (14:15) -> 8:15 ከሰዓት
        t2 = time(14, 15)
        self.assertEqual(format_time_by_lang(t2, lang="am"), "8:15 ከሰዓት")

    def test_language_switch_endpoint(self):
        response = self.client.get("/set-language/?lang=am")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get("lang"), "am")

        # Verify home page renders with Amharic translations
        response = self.client.get("/")
        self.assertContains(response, "ቀጠሮ ይያዙ")

    def test_offline_and_blocked_time_appointments(self):
        self.client.login(username="barber_admin", password="password123")
        target_date = date.today() + timedelta(days=1)

        # 1. Create a Walk-In appointment
        response = self.client.post("/dashboard/bookings/add-offline/", {
            "booking_source": "walk_in",
            "customer_name": "Solomon Walkin",
            "phone_number": "0912345678",
            "service": self.service.id,
            "barber": self.barber.id,
            "appointment_date": target_date.strftime("%Y-%m-%d"),
            "appointment_time": "11:00",
        })
        self.assertEqual(response.status_code, 302)

        # 2. Block time slot at 15:00
        response = self.client.post("/dashboard/bookings/add-offline/", {
            "booking_source": "blocked",
            "customer_name": "Lunch Break",
            "barber": self.barber.id,
            "appointment_date": target_date.strftime("%Y-%m-%d"),
            "appointment_time": "15:00",
        })
        self.assertEqual(response.status_code, 302)

        # 3. Verify public API slot logic excludes 11:00 and 15:00 for online customers
        api_response = self.client.get(f"/api/available-slots/?date={target_date.strftime('%Y-%m-%d')}&service={self.service.id}&barber={self.barber.id}")
        data = api_response.json()
        slot_values = [s["value"] for s in data["slots"]]
        self.assertNotIn("11:00", slot_values)
        self.assertNotIn("15:00", slot_values)

        # 4. Verify schedule view renders blocked and walk-in statuses
        sched_response = self.client.get(f"/dashboard/schedule/?date={target_date.strftime('%Y-%m-%d')}")
        self.assertEqual(sched_response.status_code, 200)
        self.assertContains(sched_response, "Solomon Walkin")
        self.assertContains(sched_response, "Lunch Break")


