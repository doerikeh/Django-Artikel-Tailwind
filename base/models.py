from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from django.db.models import Q
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.db.models.signals import pre_save
class UserQuerySet(models.QuerySet):
    def search(self, query=None):
        qs = self
        if query is not None:
            or_lookup = (Q(username_user__icontains=query)|Q(email__icontains=query)|Q(bio__icontains=query))
            qs = qs.filter(or_lookup).distinct()
        return qs
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_field):
        if not email:
            raise ValueError("Harus Menggunakan Email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_field)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_field):
        extra_field.setdefault("is_staff", False)
        extra_field.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_field)


    def create_superuser(self, email, password=None, **extra_field):
        extra_field.setdefault("is_staff", True)
        extra_field.setdefault("is_superuser", True)
        if extra_field.get("is_staff") is not True:
            raise ValueError(
            "superuser must have is_staff=True"
        )
        if extra_field.get("is_superuser") is not True:
            raise ValueError(
            "superuser must have is_superuser=True"
        )
        return self._create_user(email, password, **extra_field)

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)
    def search(self, query=None):
        return self.get_queryset().search(query=query)

        

class User(AbstractUser):
    username = None
    username_user = models.CharField(max_length=90, blank=False, null=False)
    image_profile = models.ImageField(upload_to="profile/", null=True, blank=True)
    image_sampul = models.ImageField(upload_to="sampul/", null=True, blank=True)
    email = models.EmailField('email address', unique=True, blank=True, null=False)
    slug = models.SlugField(blank=True, null=True)
    no_tlp = models.IntegerField(validators=[MaxValueValidator(3012)], null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()
    
    def __str__(self):
        return f"{self.email}"
    
    def get_absolute_url(self):
        return reverse("base:user-detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.username_user)
        super(User, self).save(*args, **kwargs)

class Tags(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    bio = models.CharField(max_length=300, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ArtikelQuerySet(models.QuerySet):
    def search(self, query=None):
        qs = self
        if query is not None:
            or_lookup = (Q(judul__icontains=query)|Q(isi__icontains=query))
            qs = qs.filter(or_lookup).distinct()
        return qs

class ArtikelManager(models.Manager):
    def get_queryset(self):
        return ArtikelQuerySet(self.model, using=self._db)
    def search(self, query=None):
        return self.get_queryset().search(query=query)

class Artikel(models.Model):
    judul = models.CharField(max_length=300, blank=False, null=False)
    tags = models.ManyToManyField(Tags)
    slug = models.SlugField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    isi = models.TextField()
    likes = models.ManyToManyField(User, related_name="likes")
    objects = ArtikelManager()
    media = models.FileField(upload_to="File/")

    def get_like_url(self):
        return reverse("base:like-artikel", kwargs={"slug": self.slug})

    def __str__(self):
        return self.judul
    
    def get_api_like_url(self):
        return reverse("base:like-artikel-api", kwargs={"slug": self.slug})

    def get_absolute_url(self):
        return reverse("base:detail-artikel", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.judul)
        super(Artikel, self).save(*args, **kwargs)
