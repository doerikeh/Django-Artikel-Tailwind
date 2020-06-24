from django.shortcuts import render, get_object_or_404, redirect
import logging
from django.contrib.auth import login, authenticate
from django.views.generic import ListView, DetailView, CreateView, RedirectView
from django.contrib import messages
from django.views.generic.edit import FormView
from .forms import UserCreationForm, UserEditForm, ArtikelForm, CommentForm
from .models import Artikel, User
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from itertools import chain
from django.core.mail import send_mail
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

logger = logging.getLogger(__name__)

class SingupView(FormView):
    template_name = "register.html"
    form_class = UserCreationForm

    def get_success_url(self):
        redirect_to = self.request.GET.get("next", "/")
        return redirect_to

    def form_valid(self, form):
        response = super().form_valid(form)
        form.save()
        email = form.cleaned_data.get("email")
        raw_password = form.cleaned_data.get("password1")
        logger.info(
            "New Singup for email=%s", email
        )
        user = authenticate(email=email, password=raw_password)
        login(self.request, user)
        form.send_mail()
        messages.info(
            self.request, "You Singup success"
        )
        return response

class UserDetail(DetailView):
    queryset = User.objects.all().prefetch_related("artikel_set")
    context_object_name = "user_detail"
    template_name = "detail_user.html"


class SearchView(ListView):
    template_name = "search.html"
    paginate_by = 20
    count = 0

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['count'] = self.count or 0
        context["query"] = self.request.GET.get('q')
        return context

    def get_queryset(self):
        request = self.request
        query = request.GET.get('q', None)
        if query is not None:
            user_result = User.objects.search(query)
            artikel_result = Artikel.objects.search(query)

            queryset_chain = chain(
                user_result,
                artikel_result
            )
            qs = sorted(queryset_chain,
                        key=lambda instance: instance.pk,
                        reverse=True)
            self.count = len(qs)
            return qs
        return Artikel.objects.none() and User.objects.none()

class ArtikelLike(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        slug = self.kwargs.get("slug")
        obj = get_object_or_404(Artikel, slug=slug)
        url_ = obj.get_absolute_url()
        user = self.request.user
        if user.is_authenticated:
            if user in obj.likes.all():
                obj.likes.remove(user)
            else:
                obj.likes.add(user)
        return url_

class ArtikelLikeApi(APIView):
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, slug=None, format=None):
        # slug = self.kwargs.get("slug")
        obj = get_object_or_404(Artikel, slug=slug)
        url_ = obj.get_absolute_url()
        user = self.request.user
        updated = False
        liked = False
        if user.is_authenticated():
            if user in obj.likes.all():
                liked = False
                obj.likes.remove(user)
            else:
                liked = True
                obj.likes.add(user)
            updated = True
        data = {
            "updated": updated,
            "liked": liked
        }
        return Response(data)

# def like_artikel(request):
#     artikel = get_object_or_404(Artikel, id=request.POST.get("artikel_id"))
#     artikel.likes.add(request.user)
#     return HttpResponseRedirect(artikel.get_absolute_url())

class ArtikelView(ListView):
    model = Artikel
    queryset = Artikel.objects.filter()
    context_object_name = "artikel_list"
    template_name = "home.html"

class ArtikelViewList(ListView):
    model = Artikel
    context_object_name = "artikel_list_user"
    template_name = "artikel_list.html"

    def get_queryset(self):
        return Artikel.objects.filter(user=self.request.user)


class ArtikelDetail(DetailView  ):
    model = Artikel
    template_name = "include/detail_artikel.html"
    form = CommentForm()

    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        if form.is_valid():
            artikel = self.get_object()
            form.instance.user = request.user
            form.instance.artikel = artikel
            form.save()
            return redirect(reverse("base:artikel-detail" , kwargs={"slug":artikel.slug}))




def edit(request):
    if request.method == "POST":
        user_form = UserEditForm(instance=request.user, data=request.POST, files=request.FILES)
        if user_form.is_valid():
            user_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
    context = {
        "user_form": user_form
    }
    return render(request, "user_form.html", context)
        

def artikelform(request, slug=None):
    if request.method == "POST":
        form = ArtikelForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            # message success 
            messages.success(request, "Successfully Created")
            return HttpResponseRedirect(instance.get_absolute_url())
    else:
        form = ArtikelForm()
    context = {
        "artikel_form": form,
    }
    return render(request, "artikel_form.html", context)
