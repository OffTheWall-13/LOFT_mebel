from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(ProdPhoto)
admin.site.register(ContactMessage)
admin.site.register(Customer)
admin.site.register(Basket)
admin.site.register(BasketItem)
admin.site.register(Favorites)
admin.site.register(Region)
admin.site.register(City)


@admin.register(ProdModel)
class ProdModelAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title',)

    
@admin.register(Cat)
class CatAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'parent')


@admin.register(Prod)
class ProdAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'quantity', 'price', 'discount', 'category')

