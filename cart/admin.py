from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    """Display Order Items inside the Order admin panel."""
    model = OrderItem

    extra = 0  # Prevents adding empty extra rows
    readonly_fields = ("product","price", "quantity", "item_price", "total_price_per_item")  # Make prices read-only

    def item_price(self, obj):
        """Display individual product price in the order item."""
        return f"${obj.product.price:.2f}"
    item_price.short_description = "actual Price"


class OrderAdmin(admin.ModelAdmin):
    """Customize Order display in admin."""
    list_display = ("id", "name", "email", "phone", "total_price", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "email", "phone")
    readonly_fields = ("total_price", "created_at")
    inlines = [OrderItemInline]  # Shows Order Items inline

class OrderItemAdmin(admin.ModelAdmin):
    """Customize OrderItem display in admin."""
    list_display = ("order", "product", "quantity", "item_price", "total_price_per_item")

    def item_price(self, obj):
        return f"${obj.product.price:.2f}"
    item_price.short_description = "Unit Price"

    def total_price_per_item(self, obj):
        return f"${obj.product.price * obj.quantity:.2f}"
    total_price_per_item.short_description = "Total Price"

# Register models
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
