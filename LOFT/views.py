from urllib import request

from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import login, logout
from .forms import *    
from .models import *
from .utils import BasketAuthCustomer

# Create your views here.

def main_page_view(request):
    products = Prod.objects.all().order_by('-created_at')[:12]
    categories = Cat.objects.all()
    context = {
        'products': products,
        'categories': categories,
        'title': 'Главная страница'
    }
    return render(request, 'index.html', context=context)


def product_detail_view(request, slug):
    product = get_object_or_404(Prod, slug=slug)
    products = Prod.objects.filter(category=product.category).exclude(id=product.id)[:4]
    categories = Cat.objects.all()
    context = {
        'product': product,
        'products': products,
        'categories': categories,
        'title': product.title
    }
    return render(request, 'product.html', context=context)


def category_view(request, slug):
    category = get_object_or_404(Cat, slug=slug)
    products = Prod.objects.filter(category=category)
    print(products)
    categories = Cat.objects.all()
    context = {
        'category': category,
        'products': products,
        'categories': categories,
        'title': f'Товары категории "{category.title}"'
    }
    return render(request, 'index.html', context=context)


def about_view(request):
    categories = Cat.objects.all()
    context = {
        'categories': categories,
        'title': 'О нас'
    }
    return render(request, 'about.html', context=context)


def login_user_view(request):
    categories = Cat.objects.all()
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        if user:
            login(request, user)
            return redirect('main')

    context = {
        'categories': categories,
        'title': 'Авторизация',
        'form': form,
    }
    return render(request, 'login.html', context=context)


def logout_user_view(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('main')


def register_user_view(request):
    categories = Cat.objects.all()
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        if user:
            Customer.objects.create(user, phone=form.data.get('phone'))
            login(request, user)
            return redirect('main')
    context = {
        'categories': categories,
        'title': 'Регистрация',
        'form': form,
    }

    return render(request, 'registration.html', context=context)

@login_required(login_url='login')
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES)
        if form.is_valid():
            contact_msg = ContactMessage(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['username'],
                message=form.cleaned_data['message'],
                file=form.cleaned_data.get('file')
            )
            contact_msg.save()
            return redirect('contact')
    else:
        form = ContactForm(initial={
            'name': request.user.first_name,
            'username': request.user.username,
        })
    categories = Cat.objects.all()
    context = {
        'categories': categories,
        'title': 'Связь с нами',
        'form': form,
    }
    return render(request, 'contact.html', context=context)


def basket_view(request):
    if request.user.is_authenticated:
        basket = get_object_or_404(Basket, user=request.user.customer)
        categories = Cat.objects.all()
        products = Prod.objects.all().order_by('-created_at')
        context = {
            'categories': categories,
            'title': 'Корзина',
            'basket': basket,
            'products': products,
        }
        return render(request, 'basket.html', context=context)
    else:
        return redirect('login')

@login_required(login_url='login')
def add_to_favorites_view(request, slug):
    next_page = request.META.get('HTTP_REFERER', 'main')
    if request.method == 'POST':
        favorites = Favorites.objects.get_or_create(user=request.user.customer)
        product = get_object_or_404(Prod, slug=slug)
        favorites.products.add(product)
        return redirect(next_page)
    else:
        return redirect('favorites')


def favorites_view(request):
    if request.user.is_authenticated:
        favorites = Favorites.objects.get_or_create(user=request.user.customer)
        categories = Cat.objects.all()
        context = {
            'categories': categories,
            'title': 'Избранное',
            'favorites': favorites,
        }
        return render(request, 'favorites.html', context=context)
    else:
        return redirect('login')


@login_required(login_url='login')  
def profile_view(request):
    if request.method == 'POST':
        user = get_object_or_404(User, id=request.user.id)
        edit_user_form = EditUserForm(request.POST, instance=user)
        edit_customer_form = EditCustomerForm(request.POST, instance=user.customer)
            
        if edit_user_form.is_valid() and edit_customer_form.is_valid():
            edit_user_form.save()
            edit_customer_form.save()
            
        return redirect('profile')
    
    else:
        edit_user_form = EditUserForm(instance=request.user)
        edit_customer_form = EditCustomerForm(instance=request.user.customer)
        
    categories = Cat.objects.all()
    context = {
        'edit_user_form': edit_user_form,
        'edit_customer_form': edit_customer_form,
        'user': user,
        'categories': categories,
        'title': 'Профиль'
    }
    return render(request, 'profile.html', context=context)

@login_required(login_url='login')
def basket_action(request, slug, action):
    basket = BasketAuthCustomer(request, slug, action)
    next_page = request.META.get('HTTP_REFERER', 'main')
    return redirect(next_page)


def shipping_reg_view(request):
    if request.user.is_authenticated:
        context = {
            'title': 'Доставка'
        }
        return render(request, 'shipping.html', context=context)


def search_view(request):
    if request.method == 'GET':
        context = {
            'title': 'Поиск'
        }
    return render(request, 'search.html', context=context)
