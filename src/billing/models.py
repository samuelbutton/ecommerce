from django.conf import settings
from django.db import models
from django.db.models.signals import post_save

from accounts.models import GuestEmail

User = settings.AUTH_USER_MODEL


class BillingProfileManager(models.Manager):
    def new_or_get(self, request):
        user = request.user
        created = False
        obj = None
        guest_email_id = request.session.get('guest_email_id')
        if user.is_authenticated:
            obj, created = self.model.objects.get_or_create(
                user=user, email=user.email)
        elif guest_email_id is not None:
            guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
            obj, created = self.model.objects.get_or_create(
                email=guest_email_obj.email)
        else:
            pass

        return obj, created


class BillingProfile(models.Model):
    user = models.OneToOneField(
        User, null=True, blank=True, on_delete=models.CASCADE)
    email = models.EmailField()
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = BillingProfileManager()

    def __str__(self):
        return self.email


# def billing_profile_receiver(sender, instance, created, *args, **kwargs):
#     if created:
#         print("send to stripe/braintree")
#         instance.save()


# post_save.connect(billing_profile_receiver, sender=BillingProfile)


def post_save_user_created_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(
            user=instance, email=instance.email)


post_save.connect(post_save_user_created_receiver, sender=User)
