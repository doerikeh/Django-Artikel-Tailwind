from django.shortcuts import render, get_object_or_404
import logging
from django.contrib.auth import login, authenticate
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.views.generic.edit import FormView
from .forms import UserCreationForm
from .models import Artikel, User
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from itertools import chain
from django.core.mail import send_mail




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
    model = User
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

class ArtikelView(ListView):
    model = Artikel
    queryset = Artikel.objects.all()
    context_object_name = "artikel_list"
    template_name = "home.html"


class ArtikelDetail(DetailView):
    model = Artikel
    template_name = "include/detail_artikel.html"
