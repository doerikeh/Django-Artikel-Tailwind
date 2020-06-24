from .views import (SingupView, SearchView, ArtikelDetail, ArtikelView, UserDetail, 
                    ArtikelViewList, edit, artikelform,ArtikelLike, ArtikelLikeApi)
from django.urls import path
from .forms import AuthenticatedForm
from django.contrib.auth import views as auth_views

app_name = "base"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="login.html", form_class=AuthenticatedForm), name="login"),
    path("register/", SingupView.as_view(), name='register'),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/<slug:slug>/", UserDetail.as_view(), name="user-detail"),
    path("artikel/<slug:slug>/", ArtikelDetail.as_view(), name="detail-artikel"),
    path("artikel/list/", ArtikelViewList.as_view(), name="list-artikel"),
    path("edit/", edit, name="edit"),
    path("artikel/create/", artikelform, name="artikel-form"),
    path("search/", SearchView.as_view(), name="search"),
    path("", ArtikelView.as_view(), name="home"),
    path("<slug:slug>/like/", ArtikelLike.as_view(), name="like-artikel"),
    path("api/<slug:slug>/like/", ArtikelLikeApi.as_view(), name="like-artikel-api")
]