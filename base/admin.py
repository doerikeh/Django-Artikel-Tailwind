from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AdminUser
from django.db import models
from .models import User, Tags, Artikel
from django.utils.html import format_html
from tinymce.widgets import TinyMCE

import datetime


class DateYearFilter(admin.SimpleListFilter):
    title = 'year'
    parameter_name = "date_created"

    def lookups(self, request, model_admin):
        firstyear = Tags.objects.order_by("date_created").first().date_created.year
        # firstyear = Tags.objects.order_by("date_created").first().date_created.year
        currentyear = datetime.datetime.now().year
        years = []
        for x in range(currentyear - firstyear):
            yearloop = firstyear+x
            years.insert(0,(str(currentyear), str(yearloop)))
        years.insert(0,(str(currentyear), str(currentyear)))
        return years

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(date_created__year=self.value())
        else:
            return queryset

class DateYearFilterArtikel(admin.SimpleListFilter):
    title = 'year'
    parameter_name = "date_created"

    def lookups(self, request, model_admin):
        firstyear = Artikel.objects.order_by("date_created").first().date_created.year
        # firstyear = Tags.objects.order_by("date_created").first().date_created.year
        currentyear = datetime.datetime.now().year
        years = []
        for x in range(currentyear - firstyear):
            yearloop = firstyear+x
            years.insert(0,(str(currentyear), str(yearloop)))
        years.insert(0,(str(currentyear), str(currentyear)))
        return years

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(date_created__year=self.value())
        else:
            return queryset

@admin.register(User)
class Users(AdminUser):
    fieldsets = (
        (None, {"fields":("email", "password")}),
        ("Personal info", {"fields": ("username_user","first_name", "slug","last_name", "no_tlp", "bio", "image_profile", "image_sampul")},),
        ("Permission", {"fields":("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},),
        ("Important date", {"fields": ("last_login", "date_joined")},),
    )
    
    add_fieldsets = (
        (None, {"classes":("wide",),"fields":("email", "password1", "password2"),},),
    )


    list_filter = ("is_staff", "is_superuser", "is_active")
    list_display_links = ("email",)
    prepopulated_fields = {"slug":("username_user",)}
    list_display = ("images", "email","is_staff" , "last_login",)
    search_fields = ("email", "first_name", "last_name", )
    ordering = ("email",)

    def images(self, obj):
        if obj.image_profile:
            return format_html(
                '<img src="%s" width="100" heigth="100" />' % obj.image_profile.url
            )
        return ""
    images.short_description = "User"

@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "bio","date_created")
    list_filter = (DateYearFilter,)
    search_fields = ("title", "bio")
    prepopulated_fields = {"slug":("title",)}
    
@admin.register(Artikel)
class ArtikelAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Artikel", {"fields": ["user", "judul", "slug", "media"]}),
        ("Content", {"fields": ["isi"]})
    ]

    list_display = ("user", "judul", "slug", "date_created", "date_updated", "media")
    list_filter = (DateYearFilterArtikel,)
    autocomplete_fields = ('tags',)
    search_fields = ("user", "judul", "date_created")
    prepopulated_fields = {"slug":("judul",)}
    list_max_show_all = 900
    list_per_page = 30

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }