from post.views import *
from django.urls import path, include

app_name = "post"

urlpatterns = [
    path('create/', CreatePost.as_view(), name='create'),
]