from datetime import date, datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q

from .forms import (
    ContactForm,
    BookingForm,
    ServiceForm,
    ShopInfoForm,
    GalleryImageForm,
    BarberForm,
)
from .models import (
    ShopInfo,
    Service,
    GalleryImage,
    Barber,
    Testimonial,
    Booking,
)


def is_staff_user(user):
    return user.is_authenticated and user.is_staff


def home(request):
    shop = ShopInfo.objects.first()
    services = Service.objects.all()
    gallery = GalleryImage.objects.all()
    barbers = Barber.objects.all()
    testimonials = Testimonial.objects.all().order_by("-id")

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you! Your message has been sent successfully.")
            return redirect("home")
    else:
        form = ContactForm()

    context = {
        "shop": shop,
        "services": services,
        "gallery": gallery,
        "barbers": barbers,
        "testimonials": testimonials,
        "form": form,
    }
    return render(request, "website/home.html", context)


def generate_available_slots(selected_date, service_duration=30, barber_id=None):
    today = date.today()
    max_date = today + timedelta(days=3)
    if selected_date < today or selected_date > max_date:
        return []

    # Operating hours: 09:00 AM to 08:00 PM (20:00)
    start_time = datetime.strptime("09:00", "%H:%M").time()
    end_time = datetime.strptime("20:00", "%H:%M").time()

    # Active bookings for the chosen date
    active_bookings = Booking.objects.filter(
        appointment_date=selected_date,
        status__in=["pending", "confirmed"],
    )
    if barber_id:
        active_bookings = active_bookings.filter(barber_id=barber_id)

    booked_intervals = []
    for b in active_bookings:
        b_duration = b.service.duration if (b.service and b.service.duration) else 30
        b_start = datetime.combine(selected_date, b.appointment_time)
        b_end = b_start + timedelta(minutes=b_duration)
        booked_intervals.append((b_start, b_end))

    available_slots = []
    curr_dt = datetime.combine(selected_date, start_time)
    end_dt = datetime.combine(selected_date, end_time)
    now_dt = datetime.now()
    step_minutes = 30

    while curr_dt + timedelta(minutes=service_duration) <= end_dt:
        slot_start = curr_dt
        slot_end = curr_dt + timedelta(minutes=service_duration)

        # Check if time is in the past for today
        if selected_date == today and slot_start <= now_dt:
            curr_dt += timedelta(minutes=step_minutes)
            continue

        # Check overlap
        overlap = False
        for b_start, b_end in booked_intervals:
            if not (slot_end <= b_start or slot_start >= b_end):
                overlap = True
                break

        if not overlap:
            available_slots.append(slot_start.strftime("%H:%M"))

        curr_dt += timedelta(minutes=step_minutes)

    return available_slots


def available_slots_api(request):
    date_str = request.GET.get("date")
    service_id = request.GET.get("service")
    barber_id = request.GET.get("barber")

    if not date_str or not service_id:
        return JsonResponse({"slots": [], "error": "Date and Service are required."})

    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"slots": [], "error": "Invalid date format."})

    try:
        service = Service.objects.get(id=service_id)
        duration = service.duration
    except Service.DoesNotExist:
        duration = 30

    b_id = int(barber_id) if barber_id and barber_id.isdigit() else None
    slots = generate_available_slots(selected_date, duration, b_id)

    formatted_slots = []
    for s in slots:
        t_obj = datetime.strptime(s, "%H:%M").time()
        formatted_slots.append({
            "value": s,
            "display": t_obj.strftime("%I:%M %p")
        })

    return JsonResponse({
        "slots": formatted_slots,
        "date": date_str,
        "today": date.today().strftime("%Y-%m-%d"),
        "max_date": (date.today() + timedelta(days=3)).strftime("%Y-%m-%d"),
    })


def booking_create(request):
    shop = ShopInfo.objects.first()
    services = Service.objects.all()
    barbers = Barber.objects.all()
    today = date.today()
    max_date = today + timedelta(days=3)

    initial_service = request.GET.get("service")
    initial_barber = request.GET.get("barber")

    if request.method == "POST":
        form = BookingForm(request.POST, request.FILES)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.payment_status = "pending"
            booking.status = "pending"
            booking.save()
            messages.success(request, "Your booking request has been submitted! Please wait while our barber verifies your payment.")
            return redirect("booking_success", pk=booking.pk)
        else:
            messages.error(request, "Please correct the errors below to complete your booking.")
    else:
        initial_data = {
            "appointment_date": today.strftime("%Y-%m-%d"),
        }
        if initial_service and initial_service.isdigit():
            initial_data["service"] = initial_service
        if initial_barber and initial_barber.isdigit():
            initial_data["barber"] = initial_barber

        form = BookingForm(initial=initial_data)

    context = {
        "form": form,
        "shop": shop,
        "services": services,
        "barbers": barbers,
        "today": today.strftime("%Y-%m-%d"),
        "max_date": max_date.strftime("%Y-%m-%d"),
    }
    return render(request, "website/booking.html", context)


def booking_success(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    shop = ShopInfo.objects.first()
    context = {
        "booking": booking,
        "shop": shop,
    }
    return render(request, "website/booking_success.html", context)


# ==============================================================================
# STAFF / BARBER DASHBOARD VIEWS
# ==============================================================================

def dashboard_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("dashboard_index")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect("dashboard_index")
            else:
                messages.error(request, "Access denied. Only staff members can access the barber dashboard.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "dashboard/login.html", {"form": form})


@login_required
@user_passes_test(is_staff_user)
def dashboard_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("dashboard_login")


@login_required
@user_passes_test(is_staff_user)
def dashboard_index(request):
    today = date.today()
    
    today_appointments = Booking.objects.filter(appointment_date=today).order_by("appointment_time")
    pending_payments = Booking.objects.filter(payment_status="pending").order_by("-created_at")
    upcoming_appointments = Booking.objects.filter(appointment_date__gt=today, status__in=["pending", "confirmed"]).order_by("appointment_date", "appointment_time")[:10]

    context = {
        "today_count": today_appointments.count(),
        "pending_payments_count": pending_payments.count(),
        "confirmed_count": Booking.objects.filter(status="confirmed").count(),
        "completed_count": Booking.objects.filter(status="completed").count(),
        "today_appointments": today_appointments,
        "pending_payments": pending_payments[:5],
        "upcoming_appointments": upcoming_appointments,
    }
    return render(request, "dashboard/index.html", context)


@login_required
@user_passes_test(is_staff_user)
def dashboard_bookings(request):
    status_filter = request.GET.get("status", "all")
    payment_filter = request.GET.get("payment", "all")
    search_query = request.GET.get("q", "").strip()

    bookings = Booking.objects.all()

    if status_filter != "all":
        bookings = bookings.filter(status=status_filter)

    if payment_filter != "all":
        bookings = bookings.filter(payment_status=payment_filter)

    if search_query:
        bookings = bookings.filter(
            Q(customer_name__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )

    context = {
        "bookings": bookings,
        "status_filter": status_filter,
        "payment_filter": payment_filter,
        "search_query": search_query,
    }
    return render(request, "dashboard/bookings.html", context)


@login_required
@user_passes_test(is_staff_user)
def dashboard_booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "verify_payment":
            booking.payment_status = "verified"
            booking.status = "confirmed"
            booking.save()
            messages.success(request, f"Payment for Booking #{booking.id} verified and booking confirmed!")
        elif action == "reject_payment":
            booking.payment_status = "rejected"
            booking.status = "cancelled"
            booking.save()
            messages.warning(request, f"Payment for Booking #{booking.id} rejected and booking cancelled.")
        elif action == "confirm_booking":
            booking.status = "confirmed"
            booking.save()
            messages.success(request, f"Booking #{booking.id} confirmed.")
        elif action == "cancel_booking":
            booking.status = "cancelled"
            booking.save()
            messages.warning(request, f"Booking #{booking.id} cancelled.")
        elif action == "complete_booking":
            booking.status = "completed"
            booking.save()
            messages.success(request, f"Booking #{booking.id} marked as completed.")

        return redirect("dashboard_booking_detail", pk=booking.pk)

    return render(request, "dashboard/booking_detail.html", {"booking": booking})


@login_required
@user_passes_test(is_staff_user)
def dashboard_services(request):
    services = Service.objects.all()
    edit_id = request.GET.get("edit")
    editing_service = None

    if edit_id and edit_id.isdigit():
        editing_service = get_object_or_404(Service, pk=int(edit_id))

    if request.method == "POST":
        if editing_service:
            form = ServiceForm(request.POST, instance=editing_service)
        else:
            form = ServiceForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Service saved successfully!")
            return redirect("dashboard_services")
    else:
        form = ServiceForm(instance=editing_service) if editing_service else ServiceForm()

    context = {
        "services": services,
        "form": form,
        "editing_service": editing_service,
    }
    return render(request, "dashboard/services.html", context)


@login_required
@user_passes_test(is_staff_user)
def dashboard_service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == "POST":
        try:
            service.delete()
            messages.success(request, "Service deleted successfully.")
        except Exception as e:
            messages.error(request, "Cannot delete service because historical bookings reference it.")
    return redirect("dashboard_services")


@login_required
@user_passes_test(is_staff_user)
def dashboard_gallery(request):
    images = GalleryImage.objects.all().order_by("-id")
    if request.method == "POST":
        form = GalleryImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Image uploaded to gallery.")
            return redirect("dashboard_gallery")
    else:
        form = GalleryImageForm()

    return render(request, "dashboard/gallery.html", {"images": images, "form": form})


@login_required
@user_passes_test(is_staff_user)
def dashboard_gallery_delete(request, pk):
    img = get_object_or_404(GalleryImage, pk=pk)
    if request.method == "POST":
        img.delete()
        messages.success(request, "Gallery image removed.")
    return redirect("dashboard_gallery")


@login_required
@user_passes_test(is_staff_user)
def dashboard_shop_info(request):
    shop = ShopInfo.objects.first()
    if request.method == "POST":
        if shop:
            form = ShopInfoForm(request.POST, instance=shop)
        else:
            form = ShopInfoForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Shop information and payment accounts updated.")
            return redirect("dashboard_shop_info")
    else:
        form = ShopInfoForm(instance=shop) if shop else ShopInfoForm()

    return render(request, "dashboard/shop_info.html", {"form": form, "shop": shop})