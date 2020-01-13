from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver


class TimestampleModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Lote(TimestampleModel):
    title = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, db_index=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('accounts:account-view-lote', args=[self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify('{title}-{id}'.format(title=self.title, id=self.pk))
        super(Lote, self).save(*args, **kwargs)

    class Meta:
        ordering = ['title']


class Profile(TimestampleModel):
    ADMIN = 1
    MANAGER = 1
    MEMBER = 2
    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (MANAGER, 'Manager'),
        (MEMBER, 'Member'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, null=True, blank=True)

    birthdate = models.DateField(null=True, blank=True)
    lote = models.ManyToManyField(Lote, blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    dni = models.CharField(max_length=30, blank=True)
    email = models.CharField(max_length=150, blank=True)
    image_url = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
