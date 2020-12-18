from django.urls import path

from . import views

urlpatterns = [
    path('',
         views.index,
         name='index'),
    path('group/<slug:slug>/',
         views.group_posts,
         name='group'),
    path('new/',
         views.new_post,
         name='new_post'),
     path('new_group/',
          views.new_group,
          name='new_group'),
    path('follow/',
         views.follow_index,
         name='follow_index'),
    path('<str:username>/',
         views.profile,
         name='profile'),
     path('group/<slug:slug>/edit/',
          views.group_edit,
          name='group_edit'),
    path('<str:username>/<int:post_id>/',
         views.post_view,
         name='post'),
     path('<str:username>/<int:post_id>/delete_post',
          views.delete_post,
          name='delete_post'),
     path('<str:username>/<int:post_id>/like/',
         views.post_like,
         name='post_like'),
    path('<str:username>/<int:post_id>/unlike/',
         views.post_unlike,
         name='post_unlike'),
    path('<str:username>/<int:post_id>/edit/',
         views.post_edit,
         name='post_edit'),
    path('<str:username>/<int:post_id>/comment/',
         views.add_comment,
         name='add_comment'),
    path('<str:username>/<int:post_id>/<int:comment_id>/delete_comment/',
         views.delete_comment,
         name='delete_comment'),
    path('<str:username>/follow/',
         views.profile_follow,
         name='profile_follow'),
    path('<str:username>/unfollow/',
         views.profile_unfollow,
         name='profile_unfollow'),
    ]
