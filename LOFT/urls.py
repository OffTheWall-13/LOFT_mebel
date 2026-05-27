from django.urls import path
from .views import *

urlpatterns = [
    path('', main_page_view, name='main'),
    path('product/<slug:slug>/', product_detail_view, name='product'),
    path('categories/<slug:slug>/', category_view, name='category'),
    path('about/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),
    path('basket/', basket_view, name='basket'),
    path('favorites/', favorites_view, name='favorites'),
    path('favorites/<slug:slug>/', toggle_favorite, name='toggle_favorite'),
    path('profile/', profile_view, name='profile'),
    path('login/', login_user_view, name='login'),
    path('logout/', logout_user_view, name='logout'),
    path('registration/', register_user_view, name='registration'),
    path('checkout/', checkout_view, name='checkout'),
    path('search/', search_view, name='search'),
    path('basket_action/<slug:slug>/<str:action>/', basket_action, name='basket_action'),
    path('shipping/', shipping_view, name='shipping'),
]

