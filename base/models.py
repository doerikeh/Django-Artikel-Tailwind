from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from django.db.models import Q
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.db.models.signals import pre_save
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from mirage import fields
import base64
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

    def get_absolute_url(self):
        return reverse("base:tags-list", kwargs={"slug": self.slug})

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

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    artikel = models.ForeignKey("Artikel", related_name='comments', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username_user

class Artikel(models.Model):
    judul = models.CharField(max_length=300, blank=False, null=False)
    tags = models.ManyToManyField(Tags, )
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

    @property
    def get_comments(self):
        return self.comments.all().order_by('-date_created')

    @property
    def comment_count(self):
        return Comment.objects.filter(artikel=self).count()


class AuditEntry(models.Model):
    action = models.CharField(max_length=64)
    ip = models.GenericIPAddressField(null=True)
    username = models.CharField(max_length=256, null=True)

    def __unicode__(self):
        return '{0} - {1} - {2}'.format(self.action, self.username, self.ip)

    def __str__(self):
        return '{0} - {1} - {2}'.format(self.action, self.username, self.ip)


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):  
    ip = request.META.get('REMOTE_ADDR')
    AuditEntry.objects.create(action='user_logged_in', ip=ip, username=user.username_user)


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):  
    ip = request.META.get('REMOTE_ADDR')
    AuditEntry.objects.create(action='user_logged_out', ip=ip, username=user.username_user)


@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, **kwargs):
    AuditEntry.objects.create(action='user_login_failed', username=credentials.get('username_user', None))





class MessageModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='user',
                      related_name='from_user', db_index=True)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='recipient',
                           related_name='to_user', db_index=True)
    timestamp = models.DateTimeField('timestamp', auto_now_add=True, editable=False,
                              db_index=True)
    body = fields.EncryptedTextField()
    

    def __str__(self):
        return str(self.user.username_user)


    def notify_ws_clients(self):

        notification = {
            'type': 'recieve_group_message',
            'message': '{}'.format(self.id)
        }

        channel_layer = get_channel_layer()
        print("user.id {}".format(self.user.id))
        print("user.id {}".format(self.recipient.id))

        async_to_sync(channel_layer.group_send)("{}".format(self.user.id), notification)
        async_to_sync(channel_layer.group_send)("{}".format(self.recipient.id), notification)

    def save(self, *args, **kwargs):

        new = self.id
        self.body = self.body.strip()  # Trimming whitespaces from the body
        super(MessageModel, self).save(*args, **kwargs)
        if new is None:
            self.notify_ws_clients()

    # Meta
    class Meta:
        verbose_name = 'message'
        verbose_name_plural = 'messages'
        ordering = ('-timestamp',)
