from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError

def validate_video_size(value):
    limit = 50 * 1024 * 1024  # 50MB limit
    if value.size > limit:
        raise ValidationError("Video file is too large. Max size is 50MB.")

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if self.image:
            img = Image.open(self.image)
            img = img.convert("RGB")  # Ensure it's in RGB format
            img.thumbnail((800, 800))  # Resize to a max of 800x800 pixels
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=70)  # Reduce quality to 70%
            self.image = ContentFile(buffer.getvalue(), name=self.image.name)
        super().save(*args, **kwargs)

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    addons = models.ManyToManyField('self', symmetrical=False, related_name='addon_for', blank=True)
    video = models.FileField(upload_to='product_videos/', blank=True, null=True, validators=[validate_video_size])  # Added video field



    def __str__(self):
        return self.name

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # Reviewer's name
    content = models.TextField()  # Review content
    image = models.ImageField(upload_to='review_images/', blank=True, null=True)  # Reviewer's image
    created_at = models.DateTimeField(auto_now_add=True)  # Date the review was created
    
    def __str__(self):
        return f'Review by {self.name} on {self.product.name}'
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    is_main = models.BooleanField(default=False)  # Mark this image as the main image (optional)

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"
    def save(self, *args, **kwargs):
        if self.image:
            img = Image.open(self.image)
            img = img.convert("RGB")  # Ensure it's in RGB format
            img.thumbnail((800, 800))  # Resize to a max of 800x800 pixels
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=70)  # Reduce quality to 70%
            self.image = ContentFile(buffer.getvalue(), name=self.image.name)
        super().save(*args, **kwargs)