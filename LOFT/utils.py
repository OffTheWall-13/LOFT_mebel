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
        basket, created = Basket.objects.get_or_create(user=customer)
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

    def save_order(self, shipping):
        data = self.get_basket_info()
        order = Order.objects.create(customer=data['customer'], price=data['basket_price'], shipping=shipping)
        order.save()
        for item in data['basket_products']:
            product_order = ProductOrder.objects.create(order=order, prod=item.prod, title=item.prod.title, slug=item.prod.slug,
                                                        price=item.prod.get_price(), quantity=item.quantity,
                                                        total_price=item.discounted_price)
            product_order.save()

        self.clear_basket()


    def clear_basket(self):
        products = self.get_basket_info()['basket_products']
        for item in products:
            item.prod.quantity -= item.quantity
            item.prod.save()
            item.delete()

        