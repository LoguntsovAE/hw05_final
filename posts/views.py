from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from .settings import POSTS_PER_PAGE

# # импорты для лайков
# from django.http import JsonResponse
# from django.views.decorators.http import require_POST


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'paginator': paginator}
    return render(request, 'index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'group': group, 'page': page, 'paginator': paginator}
    return render(request, 'posts/group.html', context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/new.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('index')


def profile(request, username):
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


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'post': post,
        'author': post.author,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post.html', context)


@login_required
def post_edit(request, username, post_id):
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
        return render(request, 'posts/new.html', context)
    form.save()
    return redirect('post', username, post_id)


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


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id)
    if not form.is_valid():
        return redirect('post', username, post_id)
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save() 
    return redirect('post', username, post_id)


@login_required
def delete_comment(request, username, post_id, comment_id):
    """ Функция удаления коментария его автором
    самостоятельная работа"""
    post = get_object_or_404(Post, id=post_id, author__username=username)
    comment = get_object_or_404(Comment, pk=comment_id, post=post)
    if comment.author == request.user:
        comment.delete()
    return redirect('post', username, post_id,)


@login_required
def follow_index(request):
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
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(
            user=request.user,
            author=author,
        )
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    follow = get_object_or_404(
        Follow,
        author__username=username,
        user=request.user
    )
    follow.delete()
    return redirect('profile', username)


# Не понятный джсон запрос
# Явно не оптимальная структура
# Добавлены лишние импорты
# Что за декоратор: require_POST - 
# возвращает ошибку HttpResponseNotAllowed 
# (статус ответа 405), если запрос отправлен не методом POST.
# @login_required
# @require_POST
# def post_like(request):
#     post_id = request.POST.get('id')
#     action = request.POST.get('action')
#     if post_id and action:
#         try:
#             post = Post.objects.get(id=post_id)
#             if action == 'like':
#                 post.users_like.add(request.user)
#             else:
#                 post.users_like.remove(request.user)
#             return JsonResponse({'status':'ok'})
#         except:
#             pass
#     return JsonResponse({'status':'ok'})