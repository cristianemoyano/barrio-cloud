from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User

from tinymce.models import HTMLField


class TimestampleModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Category(TimestampleModel):
    title = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, db_index=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:blog-view-category', args=[self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Category, self).save(*args, **kwargs)

    class Meta:
        ordering = ['title']


class Blog(TimestampleModel):
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250)
    summary = models.CharField(max_length=100)
    rich_body = HTMLField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image_url = models.CharField(max_length=250)
    posted = models.DateField(db_index=True, auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:blog-view-post', args=[self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Blog, self).save(*args, **kwargs)

    class Meta:
        ordering = ['posted']
