from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from coupons.models import Coupon
from shop.models import Product


class Order(models.Model):
    first_name = models.CharField(verbose_name=_('first name'), max_length=50)
    last_name = models.CharField(verbose_name=_('last name'), max_length=50)
    email = models.EmailField(verbose_name=_('e-mail'), )
    address = models.CharField(verbose_name=_('address'), max_length=250)
    postal_code = models.CharField(verbose_name=_('postal code'), max_length=20)
    city = models.CharField(verbose_name=_('city'), max_length=100)
    created = models.DateTimeField(verbose_name=_('created'), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_('updated'), auto_now=True)
    paid = models.BooleanField(verbose_name=_('paid'), default=False)
    stripe_id = models.CharField(verbose_name=_('stripe id'), max_length=250, blank=True)
    coupon = models.ForeignKey(verbose_name=_('coupon'), to=Coupon, related_name='orders', null=True, blank=True,
                               on_delete=models.SET_NULL)
    discount = models.IntegerField(verbose_name=_('discount'), default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f'Order {self.pk}'

    def get_total_cost_before_discount(self):
        return sum(item.get_cost() for item in self.items.all())

    def get_discount(self):
        if not self.discount:
            return Decimal(0)
        total_cost = self.get_total_cost_before_discount()
        return total_cost * (self.discount / Decimal(100))

    def get_total_cost(self):
        return self.get_total_cost_before_discount() - self.get_discount()

    def get_stripe_url(self):
        if not self.stripe_id:
            return ''
        if '_test_' in settings.STRIPE_SECRET_KEY:
            path = 'test/'
        else:
            path = ''
        return f'https://dashboard.stripe.com/{path}payments/{self.stripe_id}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.pk)

    def get_cost(self):
        return self.price * self.quantity
