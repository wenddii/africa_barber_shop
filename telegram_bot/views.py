import json
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def telegram_webhook(request):
    if request.method != "POST":
        return JsonResponse({"status": "method not allowed"}, status=405)

    data = json.loads(request.body)

    print(data)  # We'll replace this later

    return JsonResponse({"ok": True})