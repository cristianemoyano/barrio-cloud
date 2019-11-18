from django.urls import path
from blog import views as blog_views
from django.conf.urls import include, url

app_name = 'blog'

urlpatterns = [
    path('', blog_views.BlogView.as_view(), name='blog-index'),
    path('post/<slug:slug>/', blog_views.view_post, name='blog-view-post'),
    path('new/', blog_views.PostCreateView.as_view(), name='blog-post-new'),
    path('edit/<slug:slug>/', blog_views.PostUpdateView.as_view(), name='blog-post-edit'),
    path('category/<slug:slug>/', blog_views.view_category, name='blog-view-category'),
    # rich editor urls
    url(r'^tinymce/', include('tinymce.urls')),
]
