from django.http import JsonResponse
from django.shortcuts import render, redirect

from accounts.forms import LoginForm, GuestForm
from accounts.models import GuestEmail

from addresses.forms import AddressForm
from addresses.models import Address

from billing.models import BillingProfile
from orders.models import Order
from products.models import Product

# Create your views here.
from .models import Cart


def cart_detail_api_view(request):
    cart_obj, is_new = Cart.objects.new_or_get(request)
    products = [{
        "id": product.id,
        "url": product.get_absolute_url(),
        "name": product.name,
        "price": product.price
    } for product in cart_obj.products.all()]

    data = {
        "products": products,
        "subtotal": cart_obj.subtotal,
        "total": cart_obj.total
    }
    return JsonResponse(data)


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
            added = False
        else:
            cart_obj.products.add(product_obj)
            added = True
        request.session["cart_items"] = cart_obj.products.count()
        if request.is_ajax():
            data = {
                "added": added,
                "removed": not added,
                "countCartItems": cart_obj.products.count()
            }
            return JsonResponse(data)
            # return JsonResponse({"message": "Error 400"}, status_code=400)

    return redirect("cart:home")


def checkout_home(request):
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    order_obj = None
    if cart_created or cart_obj.products.count() == 0:
        return redirect("cart:home")

    shipping_address_id = request.session.get("shipping_address_id", None)
    billing_address_id = request.session.get("billing_address_id", None)

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(
        request)

    address_qs = None
    if billing_profile is not None:
        if request.user.is_authenticated:
            address_qs = Address.objects.filter(
                billing_profile=billing_profile)
        order_obj, order_created = Order.objects.new_or_get(
            billing_profile, cart_obj)
        if shipping_address_id:
            order_obj.shipping_address = Address.objects.get(
                id=shipping_address_id)
            del request.session["shipping_address_id"]
        if billing_address_id:
            order_obj.billing_address = Address.objects.get(
                id=billing_address_id)
            del request.session["billing_address_id"]
        if billing_address_id or shipping_address_id:
            order_obj.save()

    if request.method == "POST" and order_obj:
        "check that order is done"
        is_done = order_obj.check_done()
        if is_done:
            order_obj.mark_paid()
            request.session["cart_items"] = 0
            del request.session["cart_id"]
            return redirect("cart:success")

    context = {
        "object": order_obj,
        "billing_profile": billing_profile,
        "login_form": LoginForm(),
        "guest_form": GuestForm(),
        "address_form": AddressForm(),
        "address_qs": address_qs
    }
    return render(request, "carts/checkout.html", context)


def checkout_done_view(request):
    return render(request, "carts/checkout-done.html", {})
