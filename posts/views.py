from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import *
from bs4 import BeautifulSoup
import requests
from django.contrib import messages

# Create your views here.

def home_view(request, tag=None):
    if tag:
        posts =  Post.objects.filter(tags__slug=tag)
        tag = get_object_or_404(Tag, slug=tag)
    else:
        posts = Post.objects.all()

    categories = Tag.objects.all()
    
    context = {
        'posts' : posts,
        'categories' : categories,
        'tag' : tag,
    }
    return render(request, 'posts/home.html', context)

@login_required
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

            post.author = request.user

            post.save()
            form.save_m2m()
            return redirect('home')
        
    context = {
        "form":form,
    }
    return render(request, 'posts/post_create.html', context)

@login_required
def post_delete_view(request, pk):
    post = get_object_or_404(Post, id=pk, author=request.user)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted')
        return redirect('home')

    context = {
        "post":post,
    }
    return render(request, 'posts/post_delete.html', context)

@login_required
def post_edit_view(request, pk):
    post = get_object_or_404(Post, id=pk, author=request.user)
    form = PostEditForm(instance=post)

    if request.method == 'POST':
        form = PostEditForm(request.POST, instance=post)
        if form.is_valid:
            form.save()
            messages.success(request, 'Post updated')
            return redirect('home')
    
    context = {
        "post":post,
        "form":form
    }
    return render(request, 'posts/post_edit.html', context)


def post_page_view(request, pk):
    post = get_object_or_404(Post, id=pk)
    commentform =  CommentCreateForm()

    context = {
        "post" :post,
        "commentform ":commentform,
    }

    return render(request, 'posts/post_page.html', context)


@login_required 
def comment_sent(request, pk):
    post = get_object_or_404(Post, id=pk)
    # replyform = ReplyCreateForm()
    
    if request.method == 'POST':
        form = CommentCreateForm(request.POST)
        if form.is_valid:
            comment = form.save(commit=False)
            comment.author = request.user
            comment.parent_post = post            
            comment.save()
            
    context = {
        'post' : post,
        'comment': comment,
        # 'replyform': replyform
    }

    # return render(request, 'snippets/add_comment.html', context)
    return redirect('post', post.id)
