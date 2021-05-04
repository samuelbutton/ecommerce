import math
from django.db import models
from django.db.models.signals import pre_save, post_save

from addresses.models import Address
from billing.models import BillingProfile
from carts.models import Cart
from ecommerce.utils import unique_order_id_generator


ORDER_STATUS_CHOICES = (
    ("created", "Created"),
    ("paid", "Paid"),
    ("shipped", "Shipped"),
    ("refunded", "Refunded"),
)


class OrderManager(models.Manager):
    def new_or_get(self, billing_profile, cart_obj):
        qs = self.get_queryset().filter(
            billing_profile=billing_profile, cart=cart_obj, active=True, status="created")
        if qs.count() == 1:
            return qs.first(), False
        obj = self.model.objects.create(
            billing_profile=billing_profile,
            cart=cart_obj
        )
        return obj, True


class Order(models.Model):
    order_id = models.CharField(max_length=120, blank=True, unique=True)
    billing_profile = models.ForeignKey(
        BillingProfile, null=True, blank=True, on_delete=models.DO_NOTHING)
    shipping_address = models.ForeignKey(
        Address, related_name="shipping_address", null=True, blank=True, on_delete=models.DO_NOTHING)
    billing_address = models.ForeignKey(
        Address, related_name="billing_address", null=True, blank=True, on_delete=models.DO_NOTHING)
    cart = models.ForeignKey(Cart, on_delete=models.DO_NOTHING)
    status = models.CharField(
        max_length=120, default="created", choices=ORDER_STATUS_CHOICES)
    shipping_total = models.DecimalField(
        default=5.99, max_digits=20, decimal_places=2)
    total = models.DecimalField(
        default=0.00, max_digits=20, decimal_places=2)
    active = models.BooleanField(default=True)

    objects = OrderManager()

    def __str__(self):
        return self.order_id

    def update_total(self):
        cart_total = self.cart.total
        shipping_total = self.shipping_total
        new_total = math.fsum([cart_total, shipping_total])
        formatted_total = format(new_total, ".2f")
        self.total = new_total
        self.save()
        return new_total

    def check_done(self):
        billing_profile = self.billing_profile
        shipping_address = self.shipping_address
        billing_address = self.billing_address
        total = self.total
        if self.total <= 0:
            return False
        elif billing_profile and shipping_address and billing_address:
            return True

    def mark_paid(self):
        if self.check_done():
            self.status = "paid"
            self.save()
        return self.status


def order_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)
    qs = Order.objects.filter(cart=instance.cart, active=True).exclude(
        billing_profile=instance.billing_profile)
    if qs.exists():
        qs.update(active=False)


pre_save.connect(order_pre_save_receiver, sender=Order)


def post_save_cart_total(sender, instance, created, *args, **kwargs):
    if created:
        return

    cart_obj = instance
    qs = Order.objects.filter(cart__id=cart_obj.id)

    if qs.count() == 1:
        qs.first().update_total()


post_save.connect(post_save_cart_total, sender=Cart)


def post_save_order(sender, instance, created, *args, **kwargs):
    if created:
        instance.update_total()


post_save.connect(post_save_order, sender=Order)
