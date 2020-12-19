from django.forms import ModelForm
from django.forms.widgets import Textarea
from django.utils.translation import gettext_lazy as _
from .models import Post, Group, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ['title', 'description', 'slug']
        

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
