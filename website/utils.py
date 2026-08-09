from datetime import date, datetime, time
from ethiopian_date import EthiopianDateConverter

AMHARIC_DAYS = {
    0: "ሰኞ",
    1: "ማክሰኞ",
    2: "ረቡዕ",
    3: "ሐሙስ",
    4: "ዓርብ",
    5: "ቅዳሜ",
    6: "እሑድ",
}

AMHARIC_MONTHS = {
    1: "መስከረም",
    2: "ጥቅምት",
    3: "ኅዳር",
    4: "ታኅሣሥ",
    5: "ጥር",
    6: "የካቲት",
    7: "መጋቢት",
    8: "ሚያዝያ",
    9: "ግንቦት",
    10: "ሰኔ",
    11: "ሐምሌ",
    12: "ነሐሴ",
    13: "ጳጉሜ",
}

ENGLISH_DAYS = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}

ENGLISH_MONTHS = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


def format_date_by_lang(val, lang="en"):
    """
    Formats a Gregorian date according to the language selected.
    In Amharic ('am'), converts to Ethiopian calendar date (Bahire Hasab).
    In English ('en'), returns Gregorian date.
    """
    if not val:
        return ""

    if isinstance(val, str):
        try:
            val = datetime.strptime(val, "%Y-%m-%d").date()
        except ValueError:
            return val

    if isinstance(val, datetime):
        val = val.date()

    if lang == "am":
        try:
            eth_date = EthiopianDateConverter.to_ethiopian(val.year, val.month, val.day)
            eyear, emonth, eday = eth_date.year, eth_date.month, eth_date.day
            weekday_name = AMHARIC_DAYS.get(val.weekday(), "")
            month_name = AMHARIC_MONTHS.get(emonth, f"{emonth}")
            return f"{weekday_name}፣ {month_name} {eday} {eyear}"
        except Exception:
            return val.strftime("%Y-%m-%d")

    else:
        weekday_name = ENGLISH_DAYS.get(val.weekday(), "")
        month_name = ENGLISH_MONTHS.get(val.month, "")
        return f"{weekday_name}, {month_name} {val.day}, {val.year}"


def format_time_by_lang(val, lang="en"):
    """
    Formats a Gregorian time object/string according to selected language.
    In Amharic ('am'), converts to Ethiopian time (6-hour offset).
    In English ('en'), formats as standard 12-hour AM/PM.
    """
    if not val:
        return ""

    if isinstance(val, str):
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                val = datetime.strptime(val, fmt).time()
                break
            except ValueError:
                pass
        if isinstance(val, str):
            return val

    hour = val.hour
    minute = val.minute

    if lang == "am":
        eth_hour = (hour - 6) % 12
        if eth_hour == 0:
            eth_hour = 12

        if 6 <= hour < 12:
            period = "ጧት"
        elif 12 <= hour < 18:
            period = "ከሰዓት"
        elif 18 <= hour < 24:
            period = "ምሽት"
        else:
            period = "ሌሊት"

        return f"{eth_hour}:{minute:02d} {period}"
    else:
        return val.strftime("%I:%M %p").lstrip("0")


# TRANSLATIONS DICTIONARY FOR UI
TRANSLATIONS = {
    "en": {
        "nav_about": "About",
        "nav_services": "Services",
        "nav_barbers": "Barbers",
        "nav_reviews": "Reviews",
        "nav_gallery": "Gallery",
        "nav_contact": "Contact",
        "nav_book": "Book Appointment",
        "nav_dashboard": "Barber Login",
        "hero_eyebrow": "Premium Grooming Experience",
        "hero_title_1": "Where Every Cut",
        "hero_title_2": "Tells a Story",
        "hero_lead": "Precision cuts and luxury grooming crafted for the modern gentleman.",
        "hero_btn_book": "Book Appointment",
        "hero_btn_services": "View Services",
        "stat_clients": "Happy Clients",
        "stat_years": "Years of Craft",
        "stat_rating": "Star Rating",
        "stat_barbers": "Expert Barbers",
        "about_eyebrow": "Who We Are",
        "about_heading": "Luxury barbering, built around your style.",
        "about_p": "Paradise Barber Shop is designed for clients who want more than a quick cut. It is a polished, calm environment where every detail feels intentional, modern, and refined.",
        "services_eyebrow": "Our Services",
        "services_heading": "Crafted grooming for every detail.",
        "services_p": "Each service is delivered with care, precision, and dedicated time slots.",
        "services_book_btn": "Book This Service",
        "mins": "mins",
        "barbers_eyebrow": "Meet Our Barbers",
        "barbers_heading": "Skilled hands behind every finish.",
        "barbers_p": "Every barber at Paradise brings years of experience, sharp technique, and genuine passion for the craft.",
        "barbers_book_btn": "Book with",
        "testimonials_eyebrow": "Client Reviews",
        "testimonials_heading": "Trusted by those who value quality.",
        "gallery_eyebrow": "Gallery",
        "gallery_heading": "A look inside the experience.",
        "contact_eyebrow": "Get in Touch",
        "contact_heading": "Have Questions? Reach Out",
        "contact_p": "Send us a message or schedule your next cut directly using our online booking system.",
        "contact_btn_online": "Book Online Appointment",
        "send_message": "Send Message",
        "booking_title": "Book Your Grooming Session",
        "booking_subtitle": "Select your desired service, pick a date & time, upload your payment proof, and confirm.",
        "step_service": "1. Select Service *",
        "step_barber": "2. Select Barber (Optional)",
        "step_date": "3. Select Date * (Max 3 days ahead)",
        "step_time": "4. Select Time *",
        "choose_date_first": "-- Choose Date & Service First --",
        "select_time_default": "-- Select Available Time --",
        "no_slots": "No available slots for this date/barber",
        "your_name": "Your Full Name *",
        "phone_number": "Phone Number *",
        "notes_label": "Notes / Special Instructions (Optional)",
        "payment_title": "Payment Instructions",
        "payment_subtitle": "Please transfer the service amount before completing your booking.",
        "upload_receipt": "Upload Payment Screenshot / Receipt *",
        "upload_help": "Upload a clear image/screenshot of your transfer receipt.",
        "submit_booking": "Submit Booking & Payment Proof",
        "success_title": "Booking Submitted Successfully!",
        "success_msg": "Your appointment request has been received and is currently Pending Verification.",
        "summary_title": "Booking Summary",
        "booking_id": "Booking ID",
        "date_label": "Date",
        "time_label": "Time",
        "barber_label": "Barber",
        "service_label": "Service",
        "payment_status": "Payment Status",
        "booking_status": "Booking Status",
        "back_home": "Back to Home",
        "another_booking": "Make Another Booking",
    },
    "am": {
        "nav_about": "ስለ እኛ",
        "nav_services": "አገልግሎቶች",
        "nav_barbers": "ባርበሮች",
        "nav_reviews": "አስተያየቶች",
        "nav_gallery": "ጋለሪ",
        "nav_contact": "አድራሻ",
        "nav_book": "ቀጠሮ ይያዙ",
        "nav_dashboard": "የባርበር መግቢያ",
        "hero_eyebrow": "ልዩ የፀጉርና ፂም እንክብካቤ",
        "hero_title_1": "እያንዳንዱ ቁረጥ",
        "hero_title_2": "ታሪክ ይናገራል",
        "hero_lead": "ለዘመናዊ ወንዶች የተዘጋጀ ጥራት ያለው የፀጉርና ፂም መከርከም አገልግሎት።",
        "hero_btn_book": "ቀጠሮ ይያዙ",
        "hero_btn_services": "አገልግሎቶችን ይመልከቱ",
        "stat_clients": "ደስተኛ ደንበኞች",
        "stat_years": "የልምድ ዓመታት",
        "stat_rating": "የደረጃ አሰጣጥ",
        "stat_barbers": "ሙያተኛ ባርበሮች",
        "about_eyebrow": "ስለ እኛ",
        "about_heading": "በእርስዎ ምርጫ የተቃኘ ዘመናዊ የፀጉር ቤት።",
        "about_p": "ፓራዳይዝ ባርበር ሾፕ ፈጣን ቁረጥ ብቻ ከሚፈልጉ በላይ ለሆኑ ደንበኞች የተዘጋጀ ነው። ፀጥ ያለ፣ ዘመናዊና ምቹ አካባቢ።",
        "services_eyebrow": "አገልግሎቶቻችን",
        "services_heading": "ለእያንዳንዱ ዝርዝር ትኩረት የተሰጠው ሥራ።",
        "services_p": "እያንዳንዱ አገልግሎት በጥንቃቄ፣ በጥራትና በየተመደበው ሰዓት ይሰጣል።",
        "services_book_btn": "ይህንን አገልግሎት ይያዙ",
        "mins": "ደቂቃ",
        "barbers_eyebrow": "ባርበሮቻችንን ይወቁ",
        "barbers_heading": "ከእያንዳንዱ ሥራ ጀርባ ያሉ ባለሙያ እጆች።",
        "barbers_p": "በፓራዳይዝ የሚገኙ ባርበሮች የብዙ ዓመታት ልምድና ከፍተኛ ክህሎት አላቸው።",
        "barbers_book_btn": "ከዚህ ባርበር ጋር ይያዙ",
        "testimonials_eyebrow": "የደንበኞች አስተያየት",
        "testimonials_heading": "ጥራትን በሚያውቁ ደንበኞች የተመሰገነ።",
        "gallery_eyebrow": "ፎቶ ጋለሪ",
        "gallery_heading": "የሥራዎቻችንና የሱቃችን ገጽታ።",
        "contact_eyebrow": "ያግኙን",
        "contact_heading": "ጥያቄ አለዎት? ያግኙን",
        "contact_p": "መልእክት ይላኩልን ወይም በቀጥታ በኦንላይን ቀጠሮ ይያዙ።",
        "contact_btn_online": "በኦንላይን ቀጠሮ ይያዙ",
        "send_message": "መልእክት ላክ",
        "booking_title": "የአገልግሎት ቀጠሮ ይያዙ",
        "booking_subtitle": "የሚፈልጉትን አገልግሎት ይምረጡ፣ ቀንና ሰዓት ይምረጡ፣ የክፍያ ደረሰኝ ያስገቡና ያረጋግጡ።",
        "step_service": "1. አገልግሎት ይምረጡ *",
        "step_barber": "2. ባርበር ይምረጡ (አማራጭ)",
        "step_date": "3. ቀን ይምረጡ * (እስከ 3 ቀን ያህል)",
        "step_time": "4. ሰዓት ይምረጡ *",
        "choose_date_first": "-- አስቀድመው ቀንና አገልግሎት ይምረጡ --",
        "select_time_default": "-- ክፍት ሰዓት ይምረጡ --",
        "no_slots": "በዚህ ቀን/ባርበር ምንም ክፍት ሰዓት የለም",
        "your_name": "ሙሉ ስምዎት *",
        "phone_number": "ስልክ ቁጥር *",
        "notes_label": "ተጨማሪ ማስታወሻ (አማራጭ)",
        "payment_title": "የክፍያ መመሪያ",
        "payment_subtitle": "እባክዎን ቀጠሮውን ከማረጋገጥዎት በፊት የአገልግሎቱን ክፍያ ይክፈሉ።",
        "upload_receipt": "የክፍያ ደረሰኝ/ስክሪንሾት ይጫኑ *",
        "upload_help": "የተከፈለበትን ደረሰኝ ግልጽ ፎቶ/ስክሪንሾት ይጫኑ።",
        "submit_booking": "ቀጠሮውንና የክፍያ ማረጋገጫውን ላክ",
        "success_title": "ቀጠሮዎ በጥሩ ሁኔታ ተልኳል!",
        "success_msg": "የቀጠሮ ጥያቄዎ ደርሶናል፣ በአሁኑ ወቅት የክፍያ ማረጋገጫ በመጠባበቅ ላይ ይገኛል።",
        "summary_title": "የቀጠሮ ዝርዝር ማጠቃለያ",
        "booking_id": "የቀጠሮ ቁጥር",
        "date_label": "ቀን",
        "time_label": "ሰዓት",
        "barber_label": "ባርበር",
        "service_label": "አገልግሎት",
        "payment_status": "የክፍያ ሁኔታ",
        "booking_status": "የቀጠሮ ሁኔታ",
        "back_home": "ወደ ዋና ገጽ ተመለስ",
        "another_booking": "ሌላ ቀጠሮ ይያዙ",
    }
}


def get_translations(lang="en"):
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"])
