from django.urls import path
from .views import home_view, post_create_view


urlpatterns = [
    path('', home_view, name='home'),
    path('post/create/', post_create_view, name='post-create'),
]
