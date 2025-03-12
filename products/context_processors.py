from .models import Category

def category_links(request):
    """Add categories to the context for all templates."""
    return {'categories': Category.objects.all()}