from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User
from djmoney.models.fields import MoneyField
from tinymce.models import HTMLField


class TimestampleModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class EntryType(TimestampleModel):
    title = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, db_index=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('cash:cash-view-entry-type', args=[self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify('{title}-{id}'.format(title=self.title, id=self.pk))
        super(EntryType, self).save(*args, **kwargs)

    class Meta:
        ordering = ['title']


class Entry(TimestampleModel):
    detail = models.CharField(max_length=250)
    amount = MoneyField(max_digits=19, decimal_places=2, default_currency='ARS')
    balance = MoneyField(max_digits=19, decimal_places=2, default_currency='ARS')
    notes = HTMLField(blank=True, null=True)
    attached_file_url = models.CharField(max_length=250, blank=True, null=True)
    slug = models.SlugField(max_length=250)
    entry_type = models.ForeignKey(EntryType, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.detail

    def get_absolute_url(self):
        return reverse('cash:cash-view-entry', args=[self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify('{title}-{id}'.format(title=self.detail, id=self.pk))
        super(Entry, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_date']


class UserEntry(TimestampleModel):
    detail = models.CharField(max_length=250)
    amount = MoneyField(max_digits=19, decimal_places=2, default_currency='ARS')
    balance = MoneyField(max_digits=19, decimal_places=2, default_currency='ARS')
    notes = HTMLField(blank=True, null=True)
    attached_file_url = models.CharField(max_length=250, blank=True, null=True)
    slug = models.SlugField(max_length=250)
    entry_type = models.ForeignKey(EntryType, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='session_user')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='target_user')

    def __str__(self):
        return self.detail

    def get_absolute_url(self):
        return reverse('cash:cash-view-user-entry', args=[self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify('{title}-{id}'.format(title=self.detail, id=self.pk))
        super(UserEntry, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_date']
