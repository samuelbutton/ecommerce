from django.shortcuts import render, redirect
from django.utils.http import is_safe_url

from .forms import AddressForm
from .models import Address
from billing.models import BillingProfile


def checkout_address_create_view(request):
    form = AddressForm(request.POST or None)
    context = {
        "form": form
    }
    next_ = request.GET.get("next")
    next_post = request.POST.get("next")
    redirect_path = next_ or next_post or None
    if form.is_valid():
        print(request.POST)
        instance = form.save(commit=False)

        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(
            request)

        if billing_profile is not None:
            address_type = request.POST.get(
                "address_type", "shipping")
            instance.billing_profile = billing_profile
            instance.address_type = address_type
            instance.save()

            request.session[address_type + "_address_id"] = instance.id
            print(address_type + "_address_id")
        else:
            print("Error")
            return redirect("carts:checkout")

        if is_safe_url(redirect_path, request.get_host()):
            return redirect(redirect_path)
    return redirect("carts:checkout")


def checkout_address_reuse_view(request):
    if request.user.is_authenticated:
        context = {}
        next_ = request.GET.get("next")
        next_post = request.POST.get("next")
        redirect_path = next_ or next_post or None
        if request.method == "POST":
            print(request.POST)
            address_type = request.POST.get("address_type", "shipping")
            address_id = request.POST.get(address_type+"_address", None)
            billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(
                request)

            if address_id:
                qs = Address.objects.filter(
                    billing_profile=billing_profile, id=address_id)
                if qs.exists():
                    request.session[address_type + "_address_id"] = address_id

                if is_safe_url(redirect_path, request.get_host()):
                    return redirect(redirect_path)
    return redirect("carts:checkout")
