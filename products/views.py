from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Review
from .forms import ReviewForm



def product_list(request):
    categories = Category.objects.all()
    category_filter = request.GET.get('category')

    if category_filter:
        products = Product.objects.filter(category__id=category_filter)
    else:
        products = Product.objects.all()

    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories
    })

def index(request):
    reviews = Review.objects.all()
    categories = Category.objects.all()
    products = Product.objects.all()[0:10]
    return render(request, 'index.html', {'products': products, 'categories': categories, 'reviews':reviews})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.all()
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product  # Associate the review with the product
            review.save()
    # Calculate addon prices (original and discounted)
    else:
        form = ReviewForm()
        addons = []
        for addon in product.addons.all():
            addon_price_half = addon.price / 2  # Calculate half price
            addons.append({
                'add': addon,
                'discounted_price': addon_price_half,
            })

    return render(request, 'products/product_detail.html', {
        'product': product,
        'addons': addons,
        'form': form,
        'reviews':reviews
    })
