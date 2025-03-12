from decimal import Decimal
from django.conf import settings
from products.models import Product

class Cart:
    def __init__(self, request):
        """Initialize the cart"""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, price=0, main_product=False, main_product_id=None):
        """Add a product and update count"""
        product_id = str(product.id)
        
        if product_id not in self.cart:
            if price == 0:
                self.cart[product_id] = {'quantity': 0, 'price': str(product.price), 'main_product': main_product, 'main_product_id': main_product_id}
            else:
                self.cart[product_id] = {'quantity': 0, 'price': str(price), 'main_product': main_product, 'main_product_id': main_product_id}
        
        self.cart[product_id]['quantity'] += quantity
        if main_product:
            for pid, item in self.cart.items():
                if item['main_product_id'] == product_id:
                    item['quantity'] += quantity 
        self.save()
        self.session['cart_count'] = len(self.cart)  # Update count

    def remove(self, product):
        """Remove product and related addons from cart"""
        product_id = str(product.id)

        if product_id in self.cart:
            print(product_id,'aaaaaaaaaaaaaaaa',self.cart[product_id])
            # If it's a main product, delete it and related addons
            if self.cart[product_id]['main_product']:
                print(f"cart items: {self.cart.items()}")
                print(f"Finding related addons for main product: {product_id}")

                # Find related addons (addons with the same main_product_id)
                related_addons = [
                    pid for pid, item in self.cart.items() 
                    if item['main_product'] is False and str(item['main_product_id'] == str(product_id))
                ]
                print("Related Addons:", related_addons)

                for addon_id in related_addons:
                    del self.cart[addon_id]  # Remove the related addon
            
            
            # Remove the main product itself
            del self.cart[product_id]
            self.save()

        self.session['cart_count'] = len(self.cart)
        
    def save(self):
        """Save cart data in session"""
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def __iter__(self):
        """Iterate through cart items and retrieve products"""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            item['total_price'] = Decimal(item['price']) * item['quantity']
            yield item

    def get_total_price(self):
        """Get total price of items in the cart"""
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values() if item['quantity'] > 0)

    def clear(self):
        try:
            del self.session[settings.CART_SESSION_ID]
            self.session.modified = True  # Mark the session as modified
        except KeyError:
            # If the cart doesn't exist in the session, skip deleting it
            pass
    def get_item_quantity(self, product_id):
        """Get quantity of a specific product in the cart."""
        product_id = str(product_id)
        return self.cart.get(product_id, {}).get("quantity", 0)

    def get_item_total_price(self, product_id):
        """Get total price of a specific product in the cart."""
        product_id = str(product_id)
        item = self.cart.get(product_id)
        if item:
            return int(item["quantity"]) * float(item["price"])
        return 0