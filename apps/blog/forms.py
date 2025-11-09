from django import forms
from .models import Comment, Post


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PostForm(forms.ModelForm):
    # A simple comma-separated tags input. Users can type: tag1, tag2, tag3
    tags_input = forms.CharField(
        required=False,
        label='Tags',
        help_text='Enter tags separated by commas. New tags will be created automatically.',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. django, tutorial, tips'})
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'featured_image', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            # Leave 'content' widget to the model (CKEditor will provide its widget/media)
            'category': forms.Select(attrs={'class': 'form-select'}),
            'featured_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        # If editing an existing instance, prefill tags_input with existing tags
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            tags_qs = self.instance.tags.all()
            self.fields['tags_input'].initial = ', '.join([t.name for t in tags_qs])