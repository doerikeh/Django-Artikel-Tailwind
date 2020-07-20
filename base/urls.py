from .views import (SingupView, SearchView, ArtikelDetail, ArtikelView, UserDetail, 
                    ArtikelViewList, edit, artikelform,ArtikelLike, ArtikelLikeApi,
                    MessageModelViewSet, UserModelViewSet, chat, list_post_tags)
from django.urls import path, include
from .forms import AuthenticatedForm
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter

app_name = "base"

router = DefaultRouter()
router.register(r'message', MessageModelViewSet, basename='message-api')
router.register(r'user', UserModelViewSet, basename='user-api')

urlpatterns = [
    path(r'api/v1/', include(router.urls)),
    path("login/", auth_views.LoginView.as_view(template_name="login.html", form_class=AuthenticatedForm), name="login"),
    path("register/", SingupView.as_view(), name='register'),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/<slug:slug>/", UserDetail.as_view(), name="user-detail"),
    path("artikel/<slug:slug>/", ArtikelDetail.as_view(), name="detail-artikel"),
    path("list/", ArtikelViewList.as_view(), name="list-artikel"),
    path("edit/", edit, name="edit"),
    path("create/", artikelform, name="artikel-form"),
    path("search/", SearchView.as_view(), name="search"),
    path("chat/", chat, name="chat"),
    path("", ArtikelView.as_view(), name="home"),
    path("<slug:slug>/like/", ArtikelLike.as_view(), name="like-artikel"),
    path("api/<slug:slug>/like/", ArtikelLikeApi.as_view(), name="like-artikel-api"),
    path("tags/<slug:slug>/", list_post_tags, name="tags-list"),
    path("password/change/", auth_views.PasswordChangeView.as_view(template_name="change_password.html"), name="change_password")
]