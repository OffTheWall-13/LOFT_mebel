from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


# Create your models here.

class Cat(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название категории')
    slug = models.SlugField(unique=True, verbose_name='Слаг категории')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, verbose_name='Родитель',
                               related_name='subcats')

    def get_absolute_url(self):
        return reverse('category', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категорию'
        verbose_name_plural = 'Категории'


class ProdModel(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название модели')
    slug = models.SlugField(unique=True, verbose_name='Слаг модели')

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Модель товара'
        verbose_name_plural = 'Модели товаров'


class Prod(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название модели')
    slug = models.SlugField(unique=True, verbose_name='Слаг модели')
    prod_model = models.ForeignKey('ProdModel', on_delete=models.CASCADE, verbose_name='Модель товара', related_name='prods', null=True, blank=True)
    description = models.CharField(max_length=350, verbose_name='Краткое описание')
    quantity = models.IntegerField(default=15, verbose_name='Количество')
    price = models.IntegerField(default=200, verbose_name='Цена')
    discount = models.IntegerField(default=0, verbose_name='Скидка')
    height = models.IntegerField(default=100, verbose_name='Высота')
    width = models.IntegerField(default=100, verbose_name='Ширина')
    length = models.IntegerField(default=100, verbose_name='Длина')
    color_name = models.CharField(max_length=50, default='Чёрный', verbose_name='Название цвета')
    color_code = models.CharField(max_length=10, default='#000000', verbose_name='Код цвета')
    category = models.ForeignKey(Cat, on_delete=models.CASCADE, verbose_name='Категория', related_name='products')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('product', kwargs={'slug': self.slug})
    
    def add_to_cart(self):
        return reverse('add_to_cart', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товаров'


class ProdPhoto(models.Model):
    prod = models.ForeignKey(Prod, verbose_name='Фото товара', on_delete=models.CASCADE, related_name='prod_photo')
    image = models.ImageField(upload_to='products/', verbose_name='Фото товара')

    def __str__(self):
        return f'Фото товара {self.prod.title}'

    class Meta:
        verbose_name = 'Фото товара'
        verbose_name_plural = 'Фото товаров'


class ContactMessage(models.Model):
    name = models.CharField(max_length=150, verbose_name='Имя')
    email = models.EmailField(max_length=50, verbose_name='E-mail')
    message = models.TextField(verbose_name='Сообщение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки')
    file = models.FileField(upload_to='contact_messages/', null=True, blank=True, verbose_name='Прикрепленный файл')

    def __str__(self):
        return f"Сообщение от {self.name} <{self.email}>"

    class Meta:
        verbose_name = 'Сообщение от клиента'
        verbose_name_plural = 'Сообщения от клиентов'


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    phone = models.CharField(max_length=30, verbose_name='Номер телефона')
    region = models.CharField(max_length=100, verbose_name='Регион', null=True, blank=True)
    city = models.CharField(max_length=100, verbose_name='Город', null=True, blank=True)
    street = models.CharField(max_length=100, verbose_name='Улица', null=True, blank=True)
    home = models.CharField(max_length=100, verbose_name='Дом', null=True, blank=True)
    flat = models.CharField(max_length=100, verbose_name='Квартира №', null=True, blank=True)
    
    def __str__(self):
        return f'Покупатель {self.user.username}'

    class Meta:
        verbose_name = 'Покупателя'
        verbose_name_plural = 'Покупатели'


class Basket(models.Model):
    user = models.OneToOneField(Customer, on_delete=models.CASCADE, verbose_name='Покупатель', related_name='basket')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f'Корзина покупателя {self.user.user.username}'
    
    @property
    def total_price(self):
        return sum(prod.products_total_price for prod in self.basket_items.all())
    
    class Meta:
        verbose_name = 'Корзину'
        verbose_name_plural = 'Корзины'
        
        
class BasketItem(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, verbose_name='Корзина', related_name='basket_items')
    prod = models.ForeignKey(Prod, on_delete=models.CASCADE, verbose_name='Товар', related_name='basket_items')
    quantity = models.IntegerField(default=0, verbose_name='Количество')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')
    
    def __str__(self):
        return f'Товар {self.prod.title} в корзине покупателя {self.basket.user.user.username} в количестве {self.quantity}'
    
    @property
    def discounted_price(self):
        return self.prod.price * (1 - self.prod.discount / 100) * self.quantity
    
    @property
    def products_total_price(self):
        return self.quantity * self.prod.price

    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзинах'


class Favorites(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Покупатель', related_name='favorites')
    prod = models.ForeignKey(Prod, on_delete=models.CASCADE, verbose_name='Товар', related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    
    def __str__(self):
        return f'Товар {self.prod.title} в избранном покупателя {self.user.user.username}'
    
    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        
        
class Shipping(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Покупатель', related_name='shippings')
    phone = models.CharField(max_length=30, verbose_name='Номер получателя')
    comment = models.CharField(max_length=500, verbose_name='Комментарий к заказу', null=True, blank=True)
    region = models.ForeignKey('Region', on_delete=models.CASCADE, verbose_name='Регион')
    city = models.ForeignKey('City', on_delete=models.CASCADE, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    home = models.CharField(max_length=100, verbose_name='Дом')
    flat = models.CharField(max_length=100, verbose_name='Квартира №', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    def __str__(self):
        return f'Доставка для покупателя {self.customer.user.username} по адресу {self.address}'
    
    class Meta:
        verbose_name = 'Доставку'
        verbose_name_plural = 'Доставки'
        
        
class Region(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название региона')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'
        
        
class City(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название города')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Регион', related_name='cities')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'