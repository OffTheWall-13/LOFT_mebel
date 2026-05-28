import stripe
from urllib import request
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import login, logout
from .forms import *    
from .models import *
from .utils import BasketAuthCustomer
from django.http import JsonResponse
from django.db.models import Avg
from django.views.decorators.http import require_POST
import json
from django.db.models import Q


# Create your views here.

stripe.api_key = settings.STRIPE_SECRET_KEY


def main_page_view(request):
    products = Prod.objects.all().order_by('-created_at')
    categories = Cat.objects.all()

    if request.user.is_authenticated:
        favorites_ids = set(
            Favorites.objects.filter(user=request.user.customer).values_list('prod_id', flat=True)
        )
    else:
        favorites_ids = set()

    query = request.GET.get('q')
    not_found_message = None

    if query:
        filtered = products.filter(
            Q(title__icontains=query) |
            Q(slug__icontains=query.lower())|
            Q(description__icontains=query) |
            Q(category__title__icontains=query)|
            Q(category__slug__icontains=query.lower())|
            Q(prod_model__title__icontains=query)|
            Q(prod_model__slug__icontains=query.lower())
        ).distinct()

        if filtered.exists():
            products = filtered
        else:
            not_found_message = f"Ничего не найдено по запросу: {query}"
            products = Prod.objects.none()


    context = {
        'products': products,
        'categories': categories,
        'title': 'Главная страница',
        'favorites_ids': favorites_ids,
        'not_found_message': not_found_message,
    }
    return render(request, 'index.html', context=context)


def product_detail_view(request, slug):
    product = get_object_or_404(Prod, slug=slug)
    products = Prod.objects.filter(category=product.category).exclude(id=product.id)[:4]
    categories = Cat.objects.all()
    avg_rating = product.ratings.aggregate(Avg("value"))["value__avg"] or 0

    if request.user.is_authenticated:
        try:
            user_rating = ProductRating.objects.get(product=product, user=request.user.customer).value
        except ProductRating.DoesNotExist:
            user_rating = None
        favorites_ids = set(
            Favorites.objects.filter(user=request.user.customer).values_list('prod_id', flat=True)
        )
    else:
        favorites_ids = set()
        user_rating = None

    context = {
        'product': product,
        'products': products,
        'categories': categories,
        'title': product.title,
        'favorites_ids': favorites_ids,
        'user_rating': user_rating,
        'avg_rating': round(avg_rating, 1),
    }
    return render(request, 'product.html', context=context)


def category_view(request, slug):
    category = get_object_or_404(Cat, slug=slug)

    if category.slug == 'akcii':
        products = Prod.objects.filter(discount__gt=0)
    else:
        products = Prod.objects.filter(category=category)

    categories = Cat.objects.all()

    if request.user.is_authenticated:
        favorites_ids = set(
            Favorites.objects.filter(user=request.user.customer).values_list('prod_id', flat=True)
        )
    else:
        favorites_ids = set()

    context = {
        'category': category,
        'products': products,
        'categories': categories,
        'favorites_ids': favorites_ids,
        'title': f'Товары категории "{category.title}"'
    }
    return render(request, 'index.html', context)



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
            Customer.objects.create(user=user, phone=form.cleaned_data['phone'])
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
def favorites_view(request):
    favorites = (
        Favorites.objects
        .filter(user=request.user.customer)
        .select_related('prod')
    )
    fav_products = [fav.prod for fav in favorites]
    categories = Cat.objects.all()
    favorites_ids = set(fav.prod_id for fav in favorites)
    context = {
        'categories': categories,
        'products': fav_products,       
        'favorites_ids': favorites_ids,
        'title': 'Избранное',
    }
    return render(request, 'favorites.html', context)


@login_required
def toggle_favorite(request, slug):
    product = get_object_or_404(Prod, slug=slug)
    customer = request.user.customer

    fav = Favorites.objects.filter(user=customer, prod=product).first()
    if fav:
        fav.delete()
        status = "removed"
    else:
        Favorites.objects.create(user=customer, prod=product)
        status = "added"
    print('>>>>>>  ' + str(status))

    return JsonResponse({"status": status})


@login_required(login_url='login')  
def profile_view(request):
    if request.method == 'POST':
        user = get_object_or_404(User, id=request.user.id)
        edit_user_form = EditUserForm(request.POST, instance=user)
        edit_customer_form = EditCustomerForm(request.POST, instance=user.customer)
            
        if edit_user_form.is_valid() and edit_customer_form.is_valid():
            edit_user_form.save()
            edit_customer_form.save()
        
        else:
            form_error = [error for error in edit_user_form.errors.values()] + [error for error in edit_customer_form.errors.values()]

            
        return redirect('profile')
    
    else:
        user = request.user
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


@login_required(login_url='login')
def checkout_view(request):
    basket = BasketAuthCustomer(request)
    basket_info = basket.get_basket_info()
    if basket_info['basket_products']:
        context = basket_info
        regions = Region.objects.all()
        dict_city = {reg.pk: [[city.name, city.pk] for city in reg.cities.all()] for reg in regions}
        context['regions'] = regions
        context['title'] = 'Оформление заказа'
        context['form'] = ShippingForm()
        context['dict_city'] = dict_city
        context['categories'] = Cat.objects.all()
        return render(request, 'checkout.html', context)
    else:
        return redirect('main')


@login_required(login_url='login')
def create_checkout_session(request):
    if request.method == 'POST':
        shipping_form = ShippingForm(request.POST)
        if shipping_form.is_valid():
            basket = BasketAuthCustomer(request)
            basket_info = basket.get_basket_info()
            if basket_info['basket_products']:
                price = basket_info['basket_price']
                stripe.api_key = settings.STRIPE_SECRET_KEY
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'rub',
                            'product_data': {'name': ', '.join(i.prod.title for i in basket_info['basket_products'])},
                            'unit_amount': int(price) * 100
                        },
                        'quantity': 1
                    }],
                    mode='payment',
                    success_url=request.build_absolute_uri(reverse('success')),
                    cancel_url=request.build_absolute_uri(reverse('checkout'))
                )
                request.session[f'form_{request.user.pk}'] = request.POST
                return redirect(session.url)
        else:
            basket = BasketAuthCustomer(request)
            basket_info = basket.get_basket_info()
            regions = Region.objects.all()
            dict_city = {reg.pk: [[city.name, city.pk] for city in reg.cities.all()] for reg in regions}
            context = {
                **basket_info,
                'regions': regions,
                'dict_city': dict_city,
                'form': shipping_form,
                'categories': Cat.objects.all(),
                'title': 'Оформление заказа'
            }
            return render(request, 'checkout.html', context)


@login_required(login_url='login')
def success_payment_view(request):
    basket = BasketAuthCustomer(request)
    basket_info = basket.get_basket_info()

    try:
        form = request.session.get(f'form_{request.user.pk}')
        request.session.pop(f'form_{request.user.pk}')
    except Exception:
        form = False

    if basket_info['basket_products'] and form:
        shipping_form = ShippingForm(data=form)
        if shipping_form.is_valid():
            shipping = shipping_form.save(commit=False)
            shipping.customer = request.user.customer
            shipping.save()
            basket.save_order(shipping)
            context = {
                'title': 'Успешная оплата',
                'categories': Cat.objects.all()
            }
            return render(request, 'success.html', context)
        else:
            return redirect('checkout')
    else:
        return redirect('main')


@require_POST
def rate_product(request, slug):

    if not request.user.is_authenticated:

        return JsonResponse({
            'error': 'Необходима авторизация'
        }, status=403)

    product = get_object_or_404(Prod, slug=slug)

    data = json.loads(request.body)

    value = int(data.get('rating'))

    rating, created = ProductRating.objects.get_or_create(
        product=product,
        user=request.user.customer
    )

    rating.value = value
    rating.save()

    return JsonResponse({
        'average_rating': product.average_rating
    })


