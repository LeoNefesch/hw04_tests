# from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User
from .paginators import post_paginator


def index(request):
    posts = Post.objects.select_related('author', 'group')
    context = {
        'page_obj': post_paginator(posts, request),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    context = {
        'page_obj': post_paginator(posts, request),
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('author', 'group')
    context = {
        'author': author,
        'page_obj': post_paginator(posts, request),
        'posts': posts,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related(), id=post_id)
    context = {'post': post, }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if request.method == 'GET':
        return render(
            request,
            'posts/create_post.html',
            {'form': form, },
        )
    if not form.is_valid():
        print(form.errors, form.non_field_errors)
        return render(
            request,
            'posts/create_post.html',
            {'form': form, },
            # AssertionError: Проверьте, что на странице `/create/` выводите
            # ошибки при неправильной заполненной формы `form`
            # E         assert 400 == 200
            # E         -400
            # E         +200
            # pytest требует, чтобы у ошибки был status_code 200
            # HTTP-стандарт требует status_code 400
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400
            # status=HTTPStatus.BAD_REQUEST,
        )
    post = form.save(commit=False)
    post.text = form.cleaned_data['text']
    post.group = form.cleaned_data['group']
    post.author = request.user
    post.save()
    return redirect('posts:profile', request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post)
    if not form.is_valid():
        context = {'form': form, 'is_edit': True, 'post_id': post_id, }
        return render(request, 'posts/create_post.html', context)
    form.save()
    return redirect('posts:post_detail', post_id)
