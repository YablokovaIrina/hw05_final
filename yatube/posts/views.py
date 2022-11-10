from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Post, Group, Follow, User
from yatube.settings import POSTS_ON_PAGE


def page_obj(queryset, request):
    return Paginator(queryset, POSTS_ON_PAGE).get_page(request.GET.get('page'))


@cache_page(20, key_prefix='index_page')
def index(request):
    return render(request, 'posts/index.html', {
        'page_obj': page_obj(Post.objects.all(), request),
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', {
        'page_obj': page_obj(group.posts.all(), request),
        'group': group,
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    follow = (
        request.user.is_authenticated
        and request.user.username != username
        and Follow.objects.filter(
            author=author,
            user=request.user).exists())
    return render(request, 'posts/profile.html', {
        'page_obj': page_obj(author.posts.all(), request),
        'author': author,
        'follow': follow,
    })


def post_detail(request, post_id):
    return render(request, 'posts/post_detail.html', {
        'post': get_object_or_404(Post, pk=post_id),
        'form': CommentForm(request.POST or None),
        'comments': get_object_or_404(Post, pk=post_id).comments.all()
    })


@login_required
def post_create(request):
    form = PostForm(request.POST)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=post.author)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post.pk)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.pk)
    return render(request, 'posts/create_post.html', {
        'form': form,
        'post': post,
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post.pk)


@login_required
def follow_index(request):
    post_follow = Post.objects.filter(
        author__following__user=request.user
    )
    return render(
        request, 'posts/follow.html',
        {'page_obj': page_obj(post_follow, request)})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if Follow.objects.filter(user=request.user, author=author).exists():
        return redirect('posts:profile', username=username)
    if request.user != author:
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
