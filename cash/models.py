from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User
from djmoney.models.fields import MoneyField


class TimestampleModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Entry(TimestampleModel):
    detail = models.CharField(max_length=250)
    amount = MoneyField(max_digits=19, decimal_places=2, default_currency='ARS')
    balance = MoneyField(max_digits=19, decimal_places=2, default_currency='ARS')
    slug = models.SlugField(max_length=250)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.detail

    def get_absolute_url(self):
        return reverse('cash:cash-view-entry', args=[self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.detail)
        super(Entry, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_date']
