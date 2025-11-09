from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View
)
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.db.models import Q
from django.contrib import messages
from .models import Post, Category, Tag, Comment
from .forms import CommentForm, PostForm
from django.utils.text import slugify

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(status='published').select_related('author', 'category')

    def get_categories(self):
        return Category.objects.all()

    def get_tags(self):
        return Tag.objects.all()


class RoleRequiredMixin(UserPassesTestMixin):
    """Mixin that redirects instead of raising 403 for failed role checks.

    If the user is not authenticated, the LoginRequiredMixin will handle redirection.
    If authenticated but fails the role test, redirect to home with a message.
    """
    def handle_no_permission(self):
        # If user is authenticated but failed the role test, redirect with message
        if self.request.user.is_authenticated:
            messages.warning(self.request, 'You do not have permission to perform that action.')
            return redirect('blog:home')
        return super().handle_no_permission()
    
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionDenied:
            # Convert PermissionDenied into a friendly redirect when user is authenticated
            if request.user.is_authenticated:
                messages.warning(request, 'You do not have permission to access that page.')
                return redirect('blog:home')
            raise

class CategoryPostListView(ListView):
    model = Post
    template_name = 'blog/category_posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.filter(category=category, status='published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category, slug=self.kwargs['slug'])
        return context

class TagPostListView(ListView):
    model = Post
    template_name = 'blog/tag_posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Post.objects.filter(tags=tag, status='published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(is_approved=True)
        context['comment_form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        # Handle comment submission
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            comment = form.save(commit=False)
            comment.post = self.object
            comment.user = request.user
            # Auto-approve comments from admin/author, else require moderation
            if request.user.role in ['admin', 'author']:
                comment.is_approved = True
            else:
                comment.is_approved = False
            comment.save()
            messages.success(request, 'Your comment was submitted.' + ('' if comment.is_approved else ' It will be visible after approval.'))
            return redirect('blog:post_detail', slug=self.object.slug)
        else:
            context = self.get_context_data()
            context['comment_form'] = form
            return self.render_to_response(context)

class PostCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/post_form.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        # Save the post first (without tags)
        response = super().form_valid(form)

        # Handle comma-separated tags from the form
        tags_input = form.cleaned_data.get('tags_input', '')
        tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
        tag_objs = []
        for name in tag_names:
            slug = slugify(name)
            tag, created = Tag.objects.get_or_create(slug=slug, defaults={'name': name})
            tag_objs.append(tag)

        # Assign tags to post
        if tag_objs:
            self.object.tags.set(tag_objs)

        return response

    def test_func(self):
        return getattr(self.request.user, 'role', None) in ('admin', 'author')

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'slug': self.object.slug})

class PostUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Post
    template_name = 'blog/post_form.html'
    form_class = PostForm

    def test_func(self):
        post = self.get_object()
        return (self.request.user == post.author) or (getattr(self.request.user, 'role', None) == 'admin')

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'slug': self.object.slug})

    def form_valid(self, form):
        # Save the post instance
        response = super().form_valid(form)

        # Update tags based on tags_input
        tags_input = form.cleaned_data.get('tags_input', '')
        tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
        tag_objs = []
        for name in tag_names:
            slug = slugify(name)
            tag, created = Tag.objects.get_or_create(slug=slug, defaults={'name': name})
            tag_objs.append(tag)

        # Assign tags (can be empty to clear)
        self.object.tags.set(tag_objs)

        return response

class PostDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:home')
    template_name = 'blog/post_confirm_delete.html'

    def test_func(self):
        post = self.get_object()
        return (self.request.user == post.author) or (getattr(self.request.user, 'role', None) == 'admin')

class PostSearchView(ListView):
    model = Post
    template_name = 'blog/search_results.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Post.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query),
                status='published'
            ).distinct()
        return Post.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

class CommentApproveView(LoginRequiredMixin, RoleRequiredMixin, View):
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        comment.is_approved = True
        comment.save()
        messages.success(request, 'Comment approved successfully.')
        return redirect('blog:post_detail', slug=comment.post.slug)

    def test_func(self):
        return getattr(self.request.user, 'role', None) in ('admin', 'author')

class CommentDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'slug': self.object.post.slug})

    def test_func(self):
        comment = self.get_object()
        return (self.request.user == comment.post.author) or (getattr(self.request.user, 'role', None) == 'admin')
