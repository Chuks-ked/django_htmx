from django.shortcuts import render, redirect
from .models import Post
from .forms import PostCreateForm

# Create your views here.

def home_view(request):
    posts = Post.objects.all()
    return render(request, 'posts/home.html', {'posts':posts})


def post_create_view(request):
    form = PostCreateForm()
    if request.method == 'POST':
        form = PostCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    return render(request, 'posts/post_create.html', {'form':form})

