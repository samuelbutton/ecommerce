from django.shortcuts import render, redirect

from accounts.forms import LoginForm, GuestForm
from accounts.models import GuestEmail
from addresses.forms import AddressForm
from billing.models import BillingProfile
from orders.models import Order
from products.models import Product

# Create your views here.
from .models import Cart


def cart_home(request):
    cart_obj, is_new = Cart.objects.new_or_get(request)
    return render(request, "carts/home.html", {"cart": cart_obj})


def cart_update(request):
    product_id = request.POST.get("product_id")
    if product_id is not None:
        try:
            product_obj = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            print("No there?")
            return redirect("cart:home")
        cart_obj, is_new = Cart.objects.new_or_get(request)
        if product_obj in cart_obj.products.all():
            cart_obj.products.remove(product_obj)
        else:
            cart_obj.products.add(product_obj)
        request.session["cart_items"] = cart_obj.products.count()
    return redirect("cart:home")


def checkout_home(request):
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    order_obj = None
    if cart_created or cart_obj.products.count() == 0:
        return redirect("cart:home")

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(
        request)

    if billing_profile is not None:
        order_obj, order_created = Order.objects.new_or_get(
            billing_profile, cart_obj)

    context = {
        "object": order_obj,
        "billing_profile": billing_profile,
        "login_form": LoginForm(),
        "guest_form": GuestForm(),
        "address_form": AddressForm()
    }
    return render(request, "carts/checkout.html", context)
