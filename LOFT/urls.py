from django.urls import path
from .views import *

urlpatterns = [
    path('', main_page_view, name='main'),
    path('product/<slug:slug>/', product_detail_view, name='product'),
    path('categories/<slug:slug>/', category_view, name='category'),
    path('about/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),
    path('basket/', basket_view, name='basket'),
    path('add_to_favorites/<slug:slug>/', add_to_favorites_view, name='add_to_favorites'),
    path('favorites/', favorites_view, name='favorites'),
    path('profile/', profile_view, name='profile'),
    path('login/', login_user_view, name='login'),
    path('registration/', register_user_view, name='registration'),
    path('contact/', contact_view, name='contacts'),
    path('shipping/', shipping_reg_view, name='shipping'),
    path('search/', search_view, name='search'),
    path('basket_action/<slug:slug>/<slug:action>/', basket_action, name='basket_action'),
]

