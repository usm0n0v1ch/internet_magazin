from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, View
from app.forms import AdvancedSearchForm, ReviewForm
from app.models import Product, Category, Order, OrderItem, Review
from django.contrib import messages

class MainView(TemplateView):
    template_name = 'app/customer/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('search', '')
        context['popular_products'] = Product.objects.filter(status=Product.POPULAR)
        context['new_products'] = Product.objects.filter(status=Product.NEW)
        context['discounted_products'] = Product.objects.filter(status=Product.DISCOUNT)
        context['product_categories'] = [
            {'products': context['popular_products'], 'title': 'Популярные'},
            {'products': context['new_products'], 'title': 'Новые'},
            {'products': context['discounted_products'], 'title': 'Со скидкой'},
        ]
        if search_query:
            context['product_categories'] = []
            categories = Category.objects.all()
            for category in categories:
                products = category.product_set.filter(name__icontains=search_query)
                if products.exists():
                    context['product_categories'].append({
                        'title': category.name,
                        'products': products
                    })
        context['search_query'] = search_query
        return context

class CatalogView(TemplateView):
    template_name = 'app/customer/catalog.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.prefetch_related('product_set').all()
        return context

def search_view(request):
    search_query = request.GET.get('search', '')
    products = Product.objects.filter(name__icontains=search_query)
    return render(request, 'app/customer/search_results.html', {
        'search_query': search_query,
        'products': products,
    })

@login_required
def add_to_order(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    order, created = Order.objects.get_or_create(user=request.user, status='PENDING')
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    if not created:
        order_item.quantity += 1
    else:
        order_item.quantity = 1

    order_item.save()
    messages.success(request, f"{product.name} добавлен в заказ.")
    return redirect('main')

@login_required
def view_order(request):
    order = get_object_or_404(Order, user=request.user, status='PENDING')
    order_items = OrderItem.objects.filter(order=order)
    total = sum(item.quantity * item.price_at_order for item in order_items)

    return render(request, 'app/customer/order.html', {
        'order_items': order_items,
        'total': total,
        'order': order,
    })

@login_required
def place_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        if order_id:
            order = get_object_or_404(Order, id=order_id, user=request.user, status='PENDING')
            order.status = 'PLACED'
            order.save()
            return redirect('order_history')
    return redirect('view_order')

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'app/customer/order_history.html', {
        'orders': orders,
    })

def advanced_search(request):
    form = AdvancedSearchForm(request.GET or None)
    products = Product.objects.all()

    if form.is_valid():
        if form.cleaned_data['price_min']:
            products = products.filter(price__gte=form.cleaned_data['price_min'])
        if form.cleaned_data['price_max']:
            products = products.filter(price__lte=form.cleaned_data['price_max'])
        if form.cleaned_data['in_stock']:
            products = products.filter(in_stock=True)
        if form.cleaned_data['brands']:
            products = products.filter(brand__in=form.cleaned_data['brands'])
        if form.cleaned_data['categories']:
            products = products.filter(category__in=form.cleaned_data['categories'])
        if form.cleaned_data['has_reviews']:
            products = products.filter(review__isnull=False)
        if form.cleaned_data['average_rating_min']:
            products = products.filter(review__rating__gte=form.cleaned_data['average_rating_min'])
        if form.cleaned_data['is_new']:
            products = products.filter(status=Product.NEW)
        if form.cleaned_data['is_popular']:
            products = products.filter(status=Product.POPULAR)
        if form.cleaned_data['is_on_sale']:
            products = products.filter(status=Product.DISCOUNT)

    return render(request, 'app/customer/advanced_search.html', {'form': form, 'products': products})

class ProductDetailView(View):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        reviews = Review.objects.filter(product=product)
        form = ReviewForm()
        return render(request, 'app/customer/product_detail.html', {
            'product': product,
            'reviews': reviews,
            'form': form,
        })

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', pk=pk)
        reviews = Review.objects.filter(product=product)
        return render(request, 'app/customer/product_detail.html', {
            'product': product,
            'reviews': reviews,
            'form': form,
        })
def update_order_item(request, item_id):
    if request.method == "POST":
        order_item = get_object_or_404(OrderItem, id=item_id)
        quantity = request.POST.get('quantity', 1)
        order_item.quantity = quantity
        order_item.save()

        return redirect('view_order')