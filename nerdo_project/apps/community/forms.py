from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control border-0 bg-light-subtle',
                'rows': 3,
                'placeholder': 'What\'s on your mind?',
                'style': 'resize: none;'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
            }),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control border-0 bg-light-subtle',
                'rows': 2,
                'placeholder': 'Write a comment...',
                'style': 'resize: none;'
            }),
        }
