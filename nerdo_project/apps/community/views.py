from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Comment
from .forms import PostForm, CommentForm

@login_required
def community_home(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Your post has been shared!')
            return redirect('community_home')
    else:
        form = PostForm()

    posts = Post.objects.all()
    
    context = {
        'posts': posts,
        'form': form,
    }
    return render(request, 'community/home.html', context)

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added!')
            return redirect('post_detail', pk=pk)
    else:
        form = CommentForm()
    
    context = {
        'post': post,
        'form': form,
    }
    return render(request, 'community/post_detail.html', context)
