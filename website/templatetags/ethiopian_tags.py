from django import template
from website.utils import format_date_by_lang, format_time_by_lang, get_translations

register = template.Library()


@register.filter(name="format_date")
def format_date_filter(value, lang="en"):
    return format_date_by_lang(value, lang)


@register.filter(name="format_time")
def format_time_filter(value, lang="en"):
    return format_time_by_lang(value, lang)


@register.simple_tag
def translate(key, lang="en"):
    translations = get_translations(lang)
    return translations.get(key, key)
