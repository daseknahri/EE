from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    addons = models.ManyToManyField('self', symmetrical=False, related_name='addon_for', blank=True)
    video = models.FileField(upload_to='product_videos/', blank=True, null=True)  # Added video field



    def __str__(self):
        return self.name
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    is_main = models.BooleanField(default=False)  # Mark this image as the main image (optional)

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"