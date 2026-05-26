from .models import * 
from django.shortcuts import get_object_or_404

class BasketAuthCustomer:
    def __init__(self, request, slug=None, action=None):
        self.user = request.user
        if slug and action:
            self.action_basket_product(slug, action)

    # Метод получения информации о корзине и товарах
    def get_basket_info(self):
        customer = self.user.customer
        basket = customer.basket
        basket_products = basket.basket_items.all()
        return {
            'customer': customer,
            'basket': basket,
            'basket_products': basket_products,
            'basket_price': basket.total_price,
            'quantity_products': basket.basket_items.count()
        }

    def action_basket_product(self, slug, action):
        basket = self.get_basket_info()['basket']
        product = Prod.objects.get(slug=slug)
        product_basket, created = BasketItem.objects.get_or_create(basket=basket, prod=product)

        if action == 'add' and product_basket.quantity < product.quantity:
            product_basket.quantity += 1
            product_basket.save()
        elif action == 'remove' and product_basket.quantity > 0:
            product_basket.quantity -= 1
            product_basket.save()
            if product_basket.quantity == 0:
                product_basket.delete()
        elif action == 'delete':
            product_basket.delete()        
        