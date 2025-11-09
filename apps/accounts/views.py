from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import User
from .forms import CustomUserCreationForm
from apps.blog.models import Post
from django.contrib.auth import views as auth_views


class AccountLoginView(auth_views.LoginView):
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        messages.success(self.request, 'Logged in successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Login failed. Please check your credentials.')
        return super().form_invalid(form)

class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        # Ensure role is set and user is active
        user = form.save(commit=False)
        # role is a field on the form; ensure it's assigned
        role = form.cleaned_data.get('role')
        if role:
            user.role = role
        user.is_active = True
        user.save()
        # Let post_save signals handle group/permissions
        messages.success(self.request, 'Registration successful. Please log in.')
        # Render a small success page so confirmation is visible (avoid relying on flash messages)
        return render(self.request, 'accounts/register_success.html', {'user': user})

    def form_invalid(self, form):
        # Show form errors via messages so they are visible after redirect
        errors = form.errors.as_json()
        messages.error(self.request, 'Registration failed. Please fix the errors below.')
        return self.render_to_response(self.get_context_data(form=form))

class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(author=self.request.user).order_by('-created_at')
        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'accounts/profile_edit.html'
    fields = ['first_name', 'last_name', 'email', 'bio', 'profile_picture']
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully.')
        return super().form_valid(form)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.role in ['admin', 'author']:
            context['posts'] = Post.objects.filter(author=user).order_by('-created_at')
            context['draft_posts'] = context['posts'].filter(status='draft')
            context['published_posts'] = context['posts'].filter(status='published')
            if user.role == 'admin':
                context['all_posts'] = Post.objects.all().order_by('-created_at')
                context['total_users'] = User.objects.count()
        return context
