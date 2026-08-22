import json
import requests

from django.conf import settings
from django.core import signing
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from website.models import Booking


@csrf_exempt
def telegram_webhook(request):
    print("========== TELEGRAM WEBHOOK RECEIVED ==========")
    print("METHOD:", request.method)
    print("BODY:", request.body)

    if request.method != "POST":
        return JsonResponse(
            {"status": "method not allowed"},
            status=405
        )

    try:
        data = json.loads(request.body)

        message = data.get("message")

        if not message:
            print("No message found in Telegram update.")
            return JsonResponse({"ok": True})

        chat = message.get("chat")

        if not chat:
            print("No chat found in Telegram message.")
            return JsonResponse({"ok": True})

        chat_id = chat.get("id")
        text = message.get("text", "")

        print("CHAT ID:", chat_id)
        print("TEXT:", text)

        # Only process /start commands
        if not text.startswith("/start"):
            print("Not a /start command.")
            return JsonResponse({"ok": True})

        parts = text.split(maxsplit=1)

        # User opened the bot without the booking link
        if len(parts) < 2:
            print("No booking token provided.")

            send_telegram_message(
                chat_id,
                "Please use the Telegram reminder link from your booking confirmation."
            )

            return JsonResponse({"ok": True})

        token = parts[1]

        print("TOKEN RECEIVED:", token)
        print("TOKEN LENGTH:", len(token))

        # Validate booking token
        try:
            payload = signing.loads(
                token,
                max_age=60 * 60 * 24 * 7
            )

            print("TOKEN PAYLOAD:", payload)

        except signing.BadSignature as e:
            print("INVALID TOKEN:", e)

            send_telegram_message(
                chat_id,
                "This reminder link is invalid or has expired. "
                "Please make a new booking or contact the barbershop."
            )

            return JsonResponse({"ok": True})

        booking_id = payload.get("booking_id")

        print("BOOKING ID:", booking_id)

        if not booking_id:
            print("No booking ID found in token.")

            send_telegram_message(
                chat_id,
                "We couldn't identify your booking."
            )

            return JsonResponse({"ok": True})

        # Find booking
        try:
            booking = Booking.objects.get(id=booking_id)

            print("BOOKING FOUND:", booking.id)

        except Booking.DoesNotExist:

            print("BOOKING NOT FOUND:", booking_id)

            send_telegram_message(
                chat_id,
                "We couldn't find this booking."
            )

            return JsonResponse({"ok": True})

        # Connect Telegram account to booking
        booking.telegram_chat_id = chat_id
        booking.telegram_reminder_enabled = True

        booking.save(
            update_fields=[
                "telegram_chat_id",
                "telegram_reminder_enabled",
            ]
        )

        print("TELEGRAM CONNECTED TO BOOKING:", booking.id)

        # Safely get service name
        service_name = (
            booking.service.name
            if booking.service
            else "Selected service"
        )

        # Send confirmation
        send_telegram_message(
            chat_id,
            (
                f"Hello {booking.customer_name}! 👋\n\n"
                "Your booking has been successfully connected to Telegram. ✅\n\n"
                f"📋 Booking ID: #{booking.id}\n"
                f"📅 Date: "
                f"{booking.appointment_date.strftime('%B %d, %Y')}\n"
                f"⏰ Time: "
                f"{booking.appointment_time.strftime('%I:%M %p')}\n"
                f"💈 Service: "
                f"{service_name}\n\n"
                "Telegram reminders are now enabled. "
                "We'll remind you before your appointment."
            )
        )

        print("========== TELEGRAM WEBHOOK SUCCESS ==========")

        return JsonResponse({"ok": True})

    except Exception as e:

        print("========== TELEGRAM WEBHOOK ERROR ==========")
        print("ERROR:", repr(e))

        return JsonResponse(
            {"ok": False},
            status=500
        )


def send_telegram_message(chat_id, text):

    token = settings.TELEGRAM_BOT_TOKEN

    print("========== SENDING TELEGRAM MESSAGE ==========")
    print("TELEGRAM TOKEN EXISTS:", bool(token))
    print("CHAT ID:", chat_id)

    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN IS MISSING")

        return False

    url = (
        f"https://api.telegram.org/"
        f"bot{token}/sendMessage"
    )

    try:

        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": text,
            },
            timeout=10,
        )

        print("TELEGRAM RESPONSE STATUS:", response.status_code)
        print("TELEGRAM RESPONSE:", response.text)

        if response.ok:
            print("TELEGRAM MESSAGE SENT SUCCESSFULLY")
            return True

        print("TELEGRAM MESSAGE FAILED")
        return False

    except requests.RequestException as e:

        print("TELEGRAM REQUEST ERROR:", repr(e))

        return False