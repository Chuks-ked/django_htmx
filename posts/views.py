from django.shortcuts import render, redirect
from .models import Post
from .forms import PostCreateForm
from bs4 import BeautifulSoup
import requests
from django.contrib import messages

# Create your views here.

def home_view(request):
    posts = Post.objects.all()
    return render(request, 'posts/home.html', {'posts':posts})


def post_create_view(request):
    form = PostCreateForm()
    if request.method == 'POST':
        form = PostCreateForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)

            # Fetch the website content with headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            website = requests.get(form.data['url'], headers=headers)
            sourcecode = BeautifulSoup(website.text, 'html.parser')

            # Find image
            find_image = sourcecode.select('meta[property="og:image"]')
            if find_image:
                image = find_image[0]['content']
            else:
                find_image = sourcecode.select('img[src*="live.staticflickr.com"]')
                if find_image:
                    image = find_image[0]['src']
                else:
                    image = 'https://example.com/default-image.jpg'  # Set a default image URL
            post.image = image

            # Find title
            find_title = sourcecode.select('h1.photo-title')
            if find_title:
                title = find_title[0].text.strip()
                post.title = title
            else:
                post.title = "Untitled"  # Fallback title

            # Find artist
            find_artist = sourcecode.select('a.owner-name')
            if find_artist:
                artist = find_artist[0].text.strip()
                post.artist = artist
            else:
                post.artist = "Unknown Artist"  # Fallback artist

            post.save()
            return redirect('home')
    return render(request, 'posts/post_create.html', {'form': form})


def post_delete_view(request, pk):
    post = Post.objects.get(id=pk)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted')
        return redirect('home')

    return render(request, 'posts/post_delete.html', {'post':post})