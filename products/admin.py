from django.contrib import admin
from .models import Product, Category, ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0  # Allows adding one more image inline by default.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'created_at')
    search_fields = ('name', 'category__name')
    list_filter = ('category',)
    inlines = [ProductImageInline]



admin.site.register(ProductImage)