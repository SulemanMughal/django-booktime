from django import forms
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.forms import inlineformset_factory
from . import widgets

from . import models
import logging
logger = logging.getLogger(__name__)

class ContactForm(forms.Form):
    name = forms.CharField(label='Your name', max_length=100)
    message = forms.CharField( max_length=600, widget=forms.Textarea )

    def send_mail(self):
        logger.info("Sending email to customer service")
        message = "From: {0}\n{1}".format(
            self.cleaned_data["name"],
            self.cleaned_data["message"],
        )
        send_mail(
            "Site message",
            message,
            "site@booktime.domain",
            ["customerservice@booktime.domain"],
            fail_silently=False,
        )

class AuthenticationForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(
    strip=False, widget=forms.PasswordInput
    )
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)
    
    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        if email is not None and password:
            self.user = authenticate(
            self.request, email=email, password=password
            )
            if self.user is None:
                raise forms.ValidationError(
                "Invalid email/password combination."
                )
            logger.info(
            "Authentication successful for email=%s", email
            )
        return self.cleaned_data
    
    def get_user(self):
        return self.user


class loginForm(forms.Form):
    username = forms.CharField(label='Username', widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())



BasketLineFormSet = inlineformset_factory(
    models.Basket,
    models.BasketLine,
    fields=("quantity",),
    extra=0,
    widgets={"quantity": widgets.PlusMinusNumberInput()},
)


# BasketLineFormSet = inlineformset_factory(
#     models.Basket,
#     models.BasketLine,
#     fields=("quantity",),
#     extra=0,
#     widgets={"quantity": widgets.PlusMinusNumberInput()},
# )



class AddressSelectionForm(forms.Form):
    billing_address = forms.ModelChoiceField(
    queryset=None)
    shipping_address = forms.ModelChoiceField(
    queryset=None)
    
    def __init__(self, user, *args, **kwargs):
        super(). __init__(*args, **kwargs)
        queryset = models.Address.objects.filter(user=user)
        self.fields['billing_address'].queryset = queryset
        self.fields['shipping_address'].queryset = queryset