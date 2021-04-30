from .forms import ContactForm, LoginForm, RegisterForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model


def home_page(request):
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
        print(form.cleaned_data)

    return render(request, "contact/view.html", context)


def about_page(request):
    context = {"title": "About"}
    return render(request, "home_page.html", context)


def login_page(request):
    form = LoginForm(request.POST or None)
    context = {
        "form": form
    }

    print(request.user.is_authenticated)
    if form.is_valid():
        print(form.cleaned_data)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            context['form'] = LoginForm()
            print(request.user.is_authenticated)
            return redirect("/login")
        else:
            print("Error")

    return render(request, "auth/login.html", context)


User = get_user_model()


def register_page(request):
    form = RegisterForm(request.POST or None)
    context = {
        "form": form
    }

    if form.is_valid():
        print(form.cleaned_data)
        context['form'] = RegisterForm()
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        new_user = User.objects.create_user(username, email, password)
        print(new_user)
    return render(request, "auth/register.html", context)
