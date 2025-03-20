import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from products.models import Product
from .cart import Cart
from django.shortcuts import render, redirect
from .models import Order, OrderItem
from .forms import OrderForm

def cart_summary(request):
    """Returns cart contents for the sidebar"""
    cart = Cart(request)

    cart_items = [
        {
            "id": int(product_id),  # Convert key to integer
            "name": Product.objects.get(id=int(product_id)).category.name,
            "image": Product.objects.get(id=int(product_id)).images.first().image.url,
            "quantity": item["quantity"],
            "total_price": float(item["price"]),
            "main_product": item["main_product"],
            "main_product_id": item["main_product_id"],
        }
        for product_id, item in cart.cart.items()
    ]

    # ✅ Fix: Return correct count
    total_items = sum(item["quantity"] for item in cart.cart.values())

    return JsonResponse({
        "cart_items": cart_items,
        "cart_total": cart.get_total_price(),
        "cart_total_items": total_items  # ✅ Fix count here
    })



def update_cart(request, product_id, action):
    """Increase or decrease product quantity in cart"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        quantity_change = 1 if action == "increase" else -1
        cart.add(product, quantity=quantity_change)

         # If it's a main product, update all related addons
        if cart.cart[str(product_id)]['main_product']:
            for pid, item in cart.cart.items():
                if str(item['main_product_id']) == str(product_id):
                    cart.add(get_object_or_404(Product, id=pid), quantity=quantity_change)

        quantity = cart.get_item_quantity(product_id)
        total_price = cart.get_item_total_price(product_id)
        cart_total = cart.get_total_price()

        return JsonResponse({
            "success": True,
            "quantity": quantity,
            "total_price": total_price,
            "cart_total": cart_total
        })

    return JsonResponse({"success": False}, status=400)


def cart_detail(request):
    """View cart details"""
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})

def cart_add(request, product_id):
    """AJAX request to add product to cart"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            addon_ids = data.get("addons", [])
            

        except json.JSONDecodeError as e:
            return JsonResponse({"error": "Invalid JSON format", "details": str(e)}, status=400)


        # Add main product
        cart.add(product, quantity=1, main_product=True, main_product_id=None)

        # Add selected addons at half price
        for addon_id in addon_ids:
            addon = get_object_or_404(Product, id=addon_id)
            cart.add(addon, quantity=1, price=addon.price / 2, main_product=False, main_product_id=product.id)

        # ✅ Fix: Get total unique products in cart (not sum of all quantities)
        total_items = sum(item["quantity"] for item in cart.cart.values())

        # ✅ Fix: Ensure correct cart structure
        cart_items = [
            {
                "id": int(product_id),  # Convert key to integer
                "name": Product.objects.get(id=int(product_id)).name,
                "image": Product.objects.get(id=int(product_id)).images.first().image.url,
                "quantity": item["quantity"],
                "total_price": item["quantity"] * float(item["price"]),
                "main_product": item["main_product"],
                "main_product_id": item["main_product_id"],
            }
            for product_id, item in cart.cart.items() if item['quantity'] > 0
        ]

        return JsonResponse({
            "success": True,
            "cart_count": total_items,  # ✅ Fixed count to reflect actual items
            "cart_items": cart_items,
            "cart_total": cart.get_total_price()
        })

    return JsonResponse({"error": "Invalid request method"}, status=400)

def cart_remove(request, product_id):
    """Remove product from cart"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)

    return JsonResponse({"success": True})


from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order, OrderItem
from .forms import OrderForm
from .cart import Cart

def checkout(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)

            # If coming from Buy Now, only add that product to the order
            product_id = request.POST.get("product_id")
            offer = request.POST.get("offer")
            try:
                if product_id:

                    product = get_object_or_404(Product, id=product_id)
                    print(product)

                    # Calculate total price (base product + addons)
                    total_price = product.price
                    addon_ids = request.POST.get('addons', '').split(',')
                    print(addon_ids)
                    if addon_ids != ['']:
                        addons = Product.objects.filter(id__in=addon_ids)
                        for addon in addons:
                            total_price += addon.price / 2  # Add addon at half price
                    if offer:
                        total_price += product.price / 2

                    order.total_price = total_price
                    order.save()
                    OrderItem.objects.create(order=order, product=product, quantity=1, price=product.price)
                    if offer:
                        OrderItem.objects.create(order=order, product=product, quantity=1, price=product.price /2)
                    # Add main product and addons to OrderItem table
                    if addon_ids != ['']:
                        for addon in addons:
                            OrderItem.objects.create(order=order, product=addon, quantity=1, price=addon.price / 2)

                else:
                    # Checkout from cart
                    order.total_price = cart.get_total_price()
                    order.save()

                    # Create OrderItems for each cart item
                    for item in cart:
                        OrderItem.objects.create(order=order, product=item['product'], quantity=item['quantity'], price=item['price'])

                    # Clear the cart after successful order
                    cart.clear()

                return redirect('order_success')

            except Exception as e:
                print('somting wrong',e)
                return redirect('cart_detail')

        else:
            print('some less wrong')
            # If form is not valid, redirect back to the cart or show an error message
            return redirect('cart_detail')

    # If method is not POST, redirect to cart
    return redirect('cart_detail')



def order_success(request):
    return render(request, 'cart/order_success.html')

