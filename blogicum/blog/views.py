from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from blog.models import Post, Category, Comment
from blog.forms import PostForm, CommentForm

current_time = timezone.now()


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self, **kwargs):
        return reverse('blog:post_detail', kwargs={'pk': self.object.pk})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.object.post.pk})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.object.post.pk})


def get_post_list(queryset):
    post_list = queryset.select_related(
        'category', 'author').order_by('-pub_date').annotate(
        comment_count=Count('comments'))
    return post_list


def get_paginated_page(request, queryset):
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


class UserDetailView(DetailView):
    model = get_user_model()
    template_name = 'blog/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_object()
        post_list = get_post_list(Post.objects.filter(
            author=self.get_object()))
        page_obj = get_paginated_page(self.request, post_list)
        context['page_obj'] = page_obj
        context['username'] = self.request.user.username
        return context


class UserUpdateView(UpdateView):
    model = get_user_model()
    fields = 'first_name', 'last_name', 'email'
    success_url = reverse_lazy('blog:index')
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'blog/user.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(get_user_model(), username=request.user)
        if instance.username != request.user.username:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


def index(request):
    template = 'blog/index.html'
    post_list = get_post_list(Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__date__lte=current_time))
    page_obj = get_paginated_page(request, post_list)
    context = {'page_obj': page_obj}
    return render(request, template, context)


def post_detail(request, pk):
    template = 'blog/detail.html'
    post = get_object_or_404(Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__date__lte=current_time),
        pk=pk
    )
    context = {'post': post}
    context['form'] = CommentForm()
    context['comments'] = post.comments.select_related(
        'post').order_by('created_at')
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = get_post_list(Post.objects.filter(
        category=category,
        is_published=True,
        category__is_published=True,
        pub_date__date__lte=current_time))
    page_obj = get_paginated_page(request, post_list)
    context = {'post_list': post_list,
               'category': category, 'page_obj': page_obj}
    return render(request, template, context)


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)
