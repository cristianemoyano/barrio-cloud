from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.http import Http404
from django.shortcuts import render
from blog.models import Blog, Category

from django.views.generic.edit import CreateView


class BlogView(ListView):

    template_name = 'blog/index.html'
    model = Blog
    paginate_by = 3  # if pagination is desired
    context_object_name = 'posts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


def view_post(request, slug):
    try:
        p = Blog.objects.get(slug=slug)
    except Blog.DoesNotExist:
        raise Http404("Post does not exist")
    return render(request, 'blog/view_post.html', {'post': p})


def view_category(request, slug):
    try:
        category = Category.objects.get(slug=slug)
    except Category.DoesNotExist:
        raise Http404("Category does not exist")
    return render(
        request,
        'blog/view_category.html',
        {
            'category': category,
            'posts': Blog.objects.filter(category=category)[:5],
        }
    )


class PostCreateView(CreateView):
    model = Blog
    fields = ['title', 'rich_body', 'author', 'category', 'image_url']


class PostUpdateView(UpdateView):
    model = Blog
    fields = ['title', 'rich_body', 'author', 'category', 'image_url']
