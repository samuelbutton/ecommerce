from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from .forms import ContactForm


def home_page(request):
    # print(request.session.get('first_name', "Unknown"))
    context = {
        "title": "Hello world",
        "premium_content": "Premium"
    }
    if request.user.is_authenticated:
        context['premium_content'] = "premium2"
    return render(request, "home_page.html", context)


def contact_page(request):
    form = ContactForm(request.POST or None)
    context = {
        "title": "Contact",
        "form": form,
    }
    if form.is_valid():
        # print(form.cleaned_data)
        if request.is_ajax():
            return JsonResponse({"message": "Thank you"})

    if form.errors:
        errors = form.errors.as_json()

        if request.is_ajax():
            print("Error!")
            print(errors)
            return HttpResponse(errors, status=400)

    return render(request, "contact/view.html", context)


def about_page(request):
    context = {"title": "About"}
    return render(request, "home_page.html", context)
