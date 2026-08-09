from website.models import ShopInfo


def language_context(request):
    """
    Global context processor injecting shop branding information into all templates.
    """
    return {
        "shop": ShopInfo.objects.first(),
    }
