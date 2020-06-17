from .views import SingupView, home
from django.urls import path
from .forms import AuthenticatedForm
from django.contrib.auth import views as auth_views

app_name = "base"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="login.html", form_class=AuthenticatedForm), name="login"),
    path("register/", SingupView.as_view(), name='register'),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", home)
]