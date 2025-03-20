from django.contrib import admin
from .models import Product, Category, ProductImage, Review

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

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'created_at')
    search_fields = ('name', 'content')
    list_filter = ('created_at',)


admin.site.register(Review, ReviewAdmin)


admin.site.register(ProductImage)