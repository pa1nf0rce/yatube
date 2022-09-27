
from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    MIN_LENGTH = 20

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def clean_text(self):
        data = self.cleaned_data['text']
        if len(data) < self.MIN_LENGTH:
            self.add_error(
                'text',
                forms.ValidationError(
                    f'Минимальное количество символов - {self.MIN_LENGTH}'
                )
            )
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
