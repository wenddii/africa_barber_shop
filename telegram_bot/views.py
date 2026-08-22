import json
import requests

from django.conf import settings
from django.core import signing
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from website.models import Booking


@csrf_exempt
def telegram_webhook(request):

    if request.method != "POST":
        return JsonResponse(
            {"status": "method not allowed"},
            status=405
        )

    try:
        data = json.loads(request.body)

        message = data.get("message")

        if not message:
            return JsonResponse({"ok": True})

        chat = message.get("chat")

        if not chat:
            return JsonResponse({"ok": True})

        chat_id = chat.get("id")
        text = message.get("text", "")

        # Only process /start commands
        if not text.startswith("/start"):
            return JsonResponse({"ok": True})

        parts = text.split(maxsplit=1)

        # User opened the bot without the booking link
        if len(parts) < 2:
            send_telegram_message(
                chat_id,
                "Please use the Telegram reminder link from your booking confirmation."
            )

            return JsonResponse({"ok": True})

        token = parts[1]

        # Validate booking token
        try:
            payload = signing.loads(
                token,
                max_age=60 * 60 * 24 * 7
            )

        except signing.BadSignature:

            send_telegram_message(
                chat_id,
                "This reminder link is invalid or has expired. "
                "Please make a new booking or contact the barbershop."
            )

            return JsonResponse({"ok": True})

        booking_id = payload.get("booking_id")

        # Find booking
        try:
            booking = Booking.objects.get(id=booking_id)

        except Booking.DoesNotExist:

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

        # Send confirmation
        send_telegram_message(
            chat_id,
            (
                f"Hello {booking.customer_name}! 👋\n\n"
                "Your booking has been successfully connected to Telegram. ✅\n\n"
                f"📅 Date: "
                f"{booking.appointment_date.strftime('%B %d, %Y')}\n"
                f"⏰ Time: "
                f"{booking.appointment_time.strftime('%I:%M %p')}\n"
                f"💈 Service: "
                f"{booking.service.name}\n\n"
                "Telegram reminders are now enabled. "
                "We'll remind you before your appointment."
            )
        )

        return JsonResponse({"ok": True})

    except Exception as e:

        print("Telegram webhook error:", e)

        return JsonResponse(
            {"ok": False},
            status=500
        )


def send_telegram_message(chat_id, text):

    url = (
        f"https://api.telegram.org/"
        f"bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    response = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": text,
        },
        timeout=10,
    )

    print("Telegram response:", response.text)