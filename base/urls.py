from .views import SingupView, SearchView, ArtikelDetail, ArtikelView, UserDetail
from django.urls import path
from .forms import AuthenticatedForm
from django.contrib.auth import views as auth_views

app_name = "base"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="login.html", form_class=AuthenticatedForm), name="login"),
    path("register/", SingupView.as_view(), name='register'),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("detail/profile/<slug:slug>/", UserDetail.as_view(), name="user-detail"),
    path("detail/<slug:slug>/", ArtikelDetail.as_view(), name="detail-artikel"),
    path("search/", SearchView.as_view(), name="search"),
    path("", ArtikelView.as_view())
]