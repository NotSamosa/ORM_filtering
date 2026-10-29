from django.contrib import admin
from .models import Restaurant, Sale


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'restaurant_type', 'date_opened')
    search_fields = ('name',)
    list_filter = ('restaurant_type', 'date_opened')


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'restaurant', 'income', 'expenditure')
    list_filter = ('restaurant',)
