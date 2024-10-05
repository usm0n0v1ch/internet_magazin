from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    parent_category = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='subcategories', blank=True)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    NEW = 'NEW'
    POPULAR = 'POPULAR'
    DISCOUNT = 'DISCOUNT'

    STATUS_CHOICES = [
        (NEW, 'Новинка'),
        (POPULAR, 'Популярный'),
        (DISCOUNT, 'Со скидкой'),
    ]

    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='products/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=NEW)
    quantity = models.IntegerField()

    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.rating < 1 or self.rating > 5:
            raise ValidationError('Рейтинг должен быть от 1 до 5.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Отзыв: {self.user.username} - {self.product.name}'


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Ожидает обработки'),
        ('SHIPPED', 'Отправлен'),
        ('DELIVERED', 'Доставлен'),
        ('CANCELLED', 'Отменен'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField('Product', through='OrderItem')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f'Order {self.id} by {self.user.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.price_at_order = self.product.price
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.price_at_order = None
        super().delete(*args, **kwargs)

    def __str__(self):
        return f'{self.quantity} x {self.product.name} (Order: {self.order.id})'
