from django.forms import ModelForm
from django.forms.widgets import Textarea
from django.utils.translation import gettext_lazy as _
from .models import Comment, Post, Group


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ['title', 'description', 'slug']
        error_messages = {
            'slug': {
                'unique': _("Такой слаг существует"),
            },
        }

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите комментарий',
            })
        }
