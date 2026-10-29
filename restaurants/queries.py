from datetime import timedelta
from django.db.models import F, Q
from django.utils import timezone
from .models import Restaurant, Sale

thirty_days_ago = timezone.now().date() - timedelta(days=30)

italian_mexican_q = Q(restaurant_type=Restaurant.RestaurantType.ITALIAN) | Q(
    restaurant_type=Restaurant.RestaurantType.MEXICAN
)

recently_opened_q = Q(date_opened__gte=thirty_days_ago)
not_recently_opened_q = ~recently_opened_q

type_or_recently_opened_q = italian_mexican_q | recently_opened_q

name_contains_grill_q = Q(name__icontains='grill')
name_ends_with_cafe_q = Q(name__endswith='Cafe')

name_has_digit_q = Q(name__regex=r'\d+')

profitable_q = Q(income__gt=F('expenditure'))
sale_profitable_or_digit_restaurant_q = profitable_q | Q(restaurant__name__regex=r'\d+')

composed_sale_filter_q = (
    Q(restaurant__restaurant_type__in=[Restaurant.RestaurantType.ITALIAN, Restaurant.RestaurantType.MEXICAN])
    | Q(restaurant__name__regex=r'\d+')
) & profitable_q


def get_italian_or_mexican_restaurants():
    return Restaurant.objects.filter(italian_mexican_q)


def get_not_recently_opened_restaurants():
    return Restaurant.objects.filter(not_recently_opened_q)


def get_italian_mexican_or_recently_opened_restaurants():
    return Restaurant.objects.filter(type_or_recently_opened_q)


def get_restaurants_containing_grill():
    return Restaurant.objects.filter(name_contains_grill_q)


def get_restaurants_ending_with_cafe():
    return Restaurant.objects.filter(name_ends_with_cafe_q)


def get_restaurants_with_digits():
    return Restaurant.objects.filter(name_has_digit_q)


def get_sales_profitable_or_restaurant_has_digit():
    return Sale.objects.select_related('restaurant').filter(sale_profitable_or_digit_restaurant_q)


def get_composed_sales():
    return Sale.objects.select_related('restaurant').filter(composed_sale_filter_q)

