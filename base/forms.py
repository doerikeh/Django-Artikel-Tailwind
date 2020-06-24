from django.contrib.auth.forms import (
 UserCreationForm as DjangoUserCreationForm
)
from django.core.mail import send_mail
from django import forms
from django.contrib.auth import authenticate
import logging
from django.contrib.auth.forms import UsernameField
from .models import User, Artikel
from tinymce.widgets import TinyMCE

logger = logging.getLogger(__name__)


class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = User
        fields = ("email",)
        field_classes = {"email": UsernameField}
        def send_mail(self):
            logger.info(
            "Sending signup email for email=%s",
            self.cleaned_data["email"],
            )
            message = "Welcome{}".format(self.cleaned_data["email"])
            send_mail(
                "Welcome to Cloudimage",
                message,
                "site@climage.domain",
                [self.cleaned_data["email"]],
                fail_silently=True,
            )


class AuthenticatedForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(strip=False, widget=forms.PasswordInput)

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
                "invalid password and email"
            )
            logger.info(
                "Authenticated Success for email=%s", email
            )
        return self.cleaned_data 

    def get_user(self):
        return self.user

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("image_profile", "image_sampul","username_user", "email", "no_tlp", "bio")

        widgets = {
            "username_user": forms.TextInput(attrs={}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


class ArtikelForm(forms.ModelForm):
    class Meta:
        model = Artikel
        fields = ("media" ,"judul", "tags", "isi")
        widgets = {
            "judul": forms.TextInput(attrs={"class": "form-control"}),
            "isi":TinyMCE(attrs={'cols': 80, 'rows':50,'class': 'form-control'})
        }