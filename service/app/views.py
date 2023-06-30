from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from datetime import datetime

from app.models import Orders, Goods, Catalog
from app.forms import OrderForm, OrderDetailForm, SaleForm, SaleDetailForm, ReceivedForm, DeleteOrderForm

from app.utils import create_goods

current_time = timezone.now()
User = get_user_model()


def index(request):
    template = 'app/index.html'
    return render(request, template)


# Закупки
@login_required
def add_order_detail(request):
    number = int(request.GET.get('number'))
    quantity_name = int(request.GET.get('quantity'))
    order_date_str = request.GET.get('order_date')
    order_date = datetime.strptime(order_date_str, '%Y-%m-%d').date()
    template = 'app/add_order_detail.html'
    forms = []
    product_list = []
    
    if request.method == 'POST':
        for i in range(quantity_name):
            form = OrderDetailForm(request.POST, prefix=f'form_{i+1}')
            forms.append(form)
        if all(form.is_valid() for form in forms):
            order = Orders.objects.create(
                order_number=number,
                created_by=request.user,
                order_date=order_date,
                quantity=quantity_name
            )
            for i in range(quantity_name):
                product = Catalog.objects.get(
                    id=int(request.POST.get('form_' + str(i+1) + '-product')))
                quantity = int(request.POST.get('form_' + str(i+1) + '-quantity'))
                cost_price_RUB = request.POST.get('form_' + str(i+1) + '-cost_price_RUB')
                product_list.append(f'{product} - {quantity} ед.')
                order.product_list = ', '.join(str(item) for item in product_list)
                order.save()
                create_goods(
                    order,
                    product,
                    cost_price_RUB,
                    quantity)
            return redirect('app:orders_list')
    else:
        for i in range(quantity_name):
            form = OrderDetailForm(prefix=f'form_{i+1}')
            forms.append(form)
    
    context = {'forms': forms}
    return render(request, template, context)


@login_required
def add_order(request):
    template = 'app/add_order.html'
    form = OrderForm(request.POST or None)
    context = {'form': form}
    if form.is_valid():
        quantity = form.cleaned_data['quantity']
        order_date = form.cleaned_data['order_date']
        number = form.cleaned_data['number']
        redirect_url = reverse(
            'app:add_order_detail') + f'?quantity={quantity}&order_date={order_date}&number={number}'
        return HttpResponseRedirect(redirect_url)
    return render(request, template, context)


@login_required
def orders_list(request):
    template = 'app/orders_list.html'
    order_list = Orders.objects.select_related('created_by').filter(
        is_published=True)[:100]
    paginator = Paginator(order_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, template, context)

@login_required
def order_detail(request, pk):
    template = 'app/order_detail.html'
    order_info = Goods.objects.filter(
        is_published=True,
        order_number_id__order_number=pk).select_related('product_id').values(
        'order_number_id__order_number',
          'order_date_id__order_date',
            'product__title',
              'cost_price_RUB').annotate(count=Count('product_id'))
    context = {'order_info': order_info}
    return render(request, template, context)

@login_required
def delete_order(request, pk):
    template = 'app/edit_delete_order.html'
    instance = get_object_or_404(Orders, order_number=pk)
    form = DeleteOrderForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
        return redirect('app:orders_list')
    return render(request, template, context)

@login_required
def edit_order(request, pk):
    template = 'app/edit_delete_order.html'
    instance = get_object_or_404(Orders, order_number=pk)
    form = DeleteOrderForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        form = DeleteOrderForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('app:orders_list')
    return render(request, template, context)

@login_required
def received_order(request, pk):
    template = 'app/received_order.html'
    order = get_object_or_404(Orders, order_number=pk)
    form = ReceivedForm(instance=order)
    context = {'form': form}
    if request.method == 'POST':
        form = ReceivedForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            redirect_url = reverse('app:orders_list')
            return HttpResponseRedirect(redirect_url)
    return render(request, template, context)


#  Продажи
@login_required
def add_sale_detail(request):
    number = request.GET.get('number')
    sale_date_str = request.GET.get('sale_date')
    sale_date = datetime.strptime(sale_date_str, '%Y-%m-%d').date()
    quantity_name = int(request.GET.get('quantity'))
    payment_type = int(request.GET.get('payment_type'))

    template = 'app/add_sale_detail.html'
    forms = []
    
    if request.method == 'POST':
        for i in range(quantity_name):
            form = SaleDetailForm(request.POST, prefix=f'form_{i+1}')
            forms.append(form)
        if all(form.is_valid() for form in forms):
            for form in forms:
                sale = form.save(commit=False)
                sale.created_by = request.user
                sale.number = number
                sale.sale_date = sale_date
                sale.payment_type = payment_type
                sale.sold = True
                sale.save()
            return redirect('app:sales_list')
    else:
        for i in range(quantity_name):
            form = SaleDetailForm(prefix=f'form_{i+1}')
            forms.append(form)
    
    context = {'forms': forms}
    return render(request, template, context)


@login_required
def add_sale(request):
    template = 'app/add_sale.html'
    form = SaleForm(request.POST or None)
    context = {'form': form}
    if form.is_valid():
        number = form.cleaned_data['number']
        sale_date = form.cleaned_data['sale_date']
        quantity = form.cleaned_data['quantity']
        payment_type = form.cleaned_data['payment_type'].id
        redirect_url = reverse(
            'app:add_sale_detail') + f'?number={number}&sale_date={sale_date}&quantity={quantity}&payment_type={payment_type}'
        return HttpResponseRedirect(redirect_url)
    return render(request, template, context)


@login_required
def sales_list(request):
    template = 'app/sales_list.html'
    sales_list = Goods.objects.select_related('created_by').filter(
        is_published=True)[:100]
    context = {'sales_list': sales_list}
    return render(request, template, context)


# Профили
class UserDetailView(DetailView):
    model = get_user_model()
    template_name = 'app/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_object()
        context['username'] = self.request.user.username
        return context

"""
@login_required
def add_order_detail(request):
    number = int(request.GET.get('number'))
    quantity_name = int(request.GET.get('quantity'))
    order_date_str = request.GET.get('order_date')
    order_date = datetime.strptime(order_date_str, '%Y-%m-%d').date()
    template = 'app/add_order_detail.html'
    forms = []
    
    if request.method == 'POST':
        for i in range(quantity_name):
            form = OrderDetailForm(request.POST, prefix=f'form_{i+1}')
            forms.append(form)
        if all(form.is_valid() for form in forms):
            for form in forms:
                order = form.save(commit=False)
                order.created_by = request.user
                order.order_date = order_date
                order.number = number
                order.save()
                create_goods(
                    order.created_by,
                    order.number,
                    order.order_date,
                    order.product,
                    order.cost_price_RUB,
                    order.quantity)
            return redirect('app:orders_list')
    else:
        for i in range(quantity_name):
            form = OrderDetailForm(prefix=f'form_{i+1}')
            forms.append(form)
    
    context = {'forms': forms}
    return render(request, template, context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Orders
    form_class = OrderForm
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
"""