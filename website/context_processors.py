from website.utils import get_translations


def language_context(request):
    lang = request.session.get("lang") or request.COOKIES.get("lang") or "en"
    if lang not in ["en", "am"]:
        lang = "en"

    return {
        "current_lang": lang,
        "t": get_translations(lang),
    }
