from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm, GroupForm
from .models import Comment, Follow, Group, Post, Like, User
from .settings import POSTS_PER_PAGE


def index(request):
    """ Главная страница """
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'paginator': paginator}
    return render(request, 'index.html', context)


def profile(request, username):
    """ Страница профайла """
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    is_following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=author).exists()
    context = {
        'page': page,
        'paginator': paginator,
        'author': author,
        'is_following': is_following,
        }
    return render(request, 'posts/profile.html', context)


# БЛОК ГРУПП

def group_posts(request, slug):
    """ Странциа просмотра группы """
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/group.html', {
        'group': group,
        'page': page,
        'paginator': paginator
    })


@login_required
def new_group(request):
    """ Создание группы """
    form = GroupForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'posts/new_group.html', {'form': form})
    group = form.save(commit = False)
    group.author = request.user
    group.save()
    return redirect('index')


@login_required
def groups_view(request):
    """ Страница со всеми группами """
    groups = Group.objects.all()
    paginator = Paginator(groups, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/groups.html', {
        'groups': groups,
        'page': page,
        'paginator': paginator
    })


@login_required
def group_edit(request, slug):
    """ Редактирование группы """
    group = get_object_or_404(Group, slug=slug)
    if group.author != request.user:
         return redirect('index')
    form = GroupForm(request.POST or None, instance=group)
    if not form.is_valid():
        context = {
            'form': form,
            'group': group,
        }
        return render(request, 'posts/new_post.html', context)
    form.save()
    return redirect('group', slug)


@login_required
def group_delete(request, slug):
    """ Удаление группы """
    group = get_object_or_404(Group, slug=slug)
    if group.author == request.user:
        group.delete()
    return redirect('index')


# БЛОК ПОСТОВ

@login_required
def new_post(request):
    """ Создание нового поста """
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/new_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('index')


@login_required
def delete_post(request, username, post_id):
    """ Удаление поста """
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if post.author == request.user:
        post.delete()
    return redirect('index')


def post_view(request, username, post_id):
    """ Просмотр поста """
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm()
    comments = post.comments.all()
    is_liked = request.user.is_authenticated and Like.objects.filter(
        user=request.user,
        post=post).exists()
    context = {
        'post': post,
        'author': post.author,
        'form': form,
        'comments': comments,
        'is_liked': is_liked
    }
    return render(request, 'posts/post.html', context)


@login_required
def post_edit(request, username, post_id):
    """ Редактирование поста """
    if username != request.user.username:
        return redirect('post', username, post_id)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if not form.is_valid():
        context = {
            'form': form,
            'post': post,
        }
        return render(request, 'posts/new_post.html', context)
    form.save()
    return redirect('post', username, post_id)


 # БЛОК КОММЕНТАРИЕВ
 
@login_required
def add_comment(request, username, post_id):
    """ Создание комментария """
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('post', username, post_id)


@login_required
def comment_edit(request, username, post_id, comment_id):
    """ Редактирование комментария """
    post = get_object_or_404(Post, id=post_id, author__username=username)
    comment = get_object_or_404(Comment, pk=comment_id, post=post)
    if comment.author != request.user:
        return redirect('post', username, post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if not form.is_valid():
        context = {
            'form': form,
            'comment': comment,
        }
        return render(request, 'posts/new_post.html', context)
    form.save()
    return redirect('post', username, post_id)


@login_required
def delete_comment(request, username, post_id, comment_id):
    """ Удаление комментария"""
    post = get_object_or_404(Post, id=post_id, author__username=username)
    comment = get_object_or_404(Comment, pk=comment_id, post=post)
    if comment.author == request.user:
        comment.delete()
    return redirect('post', username, post_id,)


# БЛОК ЛАЙКОВ

@login_required
def post_like(request, username, post_id):
    """ Поставить лайк """
    post = get_object_or_404(Post, author__username=username, id=post_id)
    Like.objects.get_or_create(post=post, user=request.user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def post_unlike(request, username, post_id):
    """ Удалить лайк """
    post = get_object_or_404(Post, author__username=username, id=post_id)
    post.likes.filter(user=request.user).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


# БЛОК ПОДПИСКИ

@login_required
def follow_index(request):
    """ Страница подписок """
    posts = Post.objects.filter(
        author__following__user=request.user)
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/follow.html', {
        'page': page,
        'paginator': paginator,
    })


@login_required
def profile_follow(request, username):
    """ Функция подписки """
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(
            user=request.user,
            author=author,
        )
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    """ Функция отписки """
    follow = get_object_or_404(
        Follow,
        author__username=username,
        user=request.user
    )
    follow.delete()
    return redirect('profile', username)

# ОШИБКИ СЕРВЕРА

def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(
        request,
        'misc/500.html',
        status=500)
