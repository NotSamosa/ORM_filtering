from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from restaurants.models import Restaurant, Sale


class Command(BaseCommand):
    help = "Populate database with sample Restaurant and Sale data"

    def handle(self, *args, **options):
        self.stdout.write("Clearing existing data...")
        Sale.objects.all().delete()
        Restaurant.objects.all().delete()

        today = timezone.now().date()

        restaurant_definitions = [
            {
                "name": "Luigi's Italian Grill",
                "restaurant_type": Restaurant.RestaurantType.ITALIAN,
                "date_opened": today - timedelta(days=10),
            },
            {
                "name": "Taco Fiesta 24",
                "restaurant_type": Restaurant.RestaurantType.MEXICAN,
                "date_opened": today - timedelta(days=45),
            },
            {
                "name": "Downtown Smokehouse & GRILL",
                "restaurant_type": Restaurant.RestaurantType.AMERICAN,
                "date_opened": today - timedelta(days=15),
            },
            {
                "name": "Bella Roma Cafe",
                "restaurant_type": Restaurant.RestaurantType.ITALIAN,
                "date_opened": today - timedelta(days=90),
            },
            {
                "name": "Route 66 Diner & Cafe",
                "restaurant_type": Restaurant.RestaurantType.AMERICAN,
                "date_opened": today - timedelta(days=200),
            },
            {
                "name": "Cantina El Paso",
                "restaurant_type": Restaurant.RestaurantType.MEXICAN,
                "date_opened": today - timedelta(days=8),
            },
            {
                "name": "Golden Dragon 88",
                "restaurant_type": Restaurant.RestaurantType.CHINESE,
                "date_opened": today - timedelta(days=150),
            },
            {
                "name": "Cafe Royale",
                "restaurant_type": Restaurant.RestaurantType.FRENCH,
                "date_opened": today - timedelta(days=500),
            },
            {
                "name": "Spice Route 7",
                "restaurant_type": Restaurant.RestaurantType.INDIAN,
                "date_opened": today - timedelta(days=18),
            },
            {
                "name": "Charcoal Grill & Bar",
                "restaurant_type": Restaurant.RestaurantType.AMERICAN,
                "date_opened": today - timedelta(days=60),
            },
            {
                "name": "Tuscany Corner Cafe",
                "restaurant_type": Restaurant.RestaurantType.ITALIAN,
                "date_opened": today - timedelta(days=350),
            },
            {
                "name": "Speedy Burger 365",
                "restaurant_type": Restaurant.RestaurantType.FAST_FOOD,
                "date_opened": today - timedelta(days=25),
            },
        ]

        restaurants = {}
        for r_data in restaurant_definitions:
            r = Restaurant.objects.create(**r_data)
            restaurants[r.name] = r

        self.stdout.write(self.style.SUCCESS(f"Created {len(restaurants)} restaurants."))

        sales_data = [
            {"restaurant": restaurants["Luigi's Italian Grill"], "income": Decimal("15000.00"), "expenditure": Decimal("9000.00")},
            {"restaurant": restaurants["Luigi's Italian Grill"], "income": Decimal("6000.00"), "expenditure": Decimal("7500.00")},
            {"restaurant": restaurants["Taco Fiesta 24"], "income": Decimal("12500.00"), "expenditure": Decimal("8000.00")},
            {"restaurant": restaurants["Taco Fiesta 24"], "income": Decimal("4000.00"), "expenditure": Decimal("6200.00")},
            {"restaurant": restaurants["Downtown Smokehouse & GRILL"], "income": Decimal("22000.00"), "expenditure": Decimal("14000.00")},
            {"restaurant": restaurants["Downtown Smokehouse & GRILL"], "income": Decimal("8500.00"), "expenditure": Decimal("9200.00")},
            {"restaurant": restaurants["Bella Roma Cafe"], "income": Decimal("7500.00"), "expenditure": Decimal("9800.00")},
            {"restaurant": restaurants["Bella Roma Cafe"], "income": Decimal("5000.00"), "expenditure": Decimal("5000.00")},
            {"restaurant": restaurants["Route 66 Diner & Cafe"], "income": Decimal("18000.00"), "expenditure": Decimal("11000.00")},
            {"restaurant": restaurants["Route 66 Diner & Cafe"], "income": Decimal("3500.00"), "expenditure": Decimal("5500.00")},
            {"restaurant": restaurants["Cantina El Paso"], "income": Decimal("16500.00"), "expenditure": Decimal("10200.00")},
            {"restaurant": restaurants["Golden Dragon 88"], "income": Decimal("8200.00"), "expenditure": Decimal("10500.00")},
            {"restaurant": restaurants["Cafe Royale"], "income": Decimal("9000.00"), "expenditure": Decimal("11500.00")},
            {"restaurant": restaurants["Spice Route 7"], "income": Decimal("14000.00"), "expenditure": Decimal("8200.00")},
            {"restaurant": restaurants["Charcoal Grill & Bar"], "income": Decimal("19000.00"), "expenditure": Decimal("12000.00")},
            {"restaurant": restaurants["Tuscany Corner Cafe"], "income": Decimal("4800.00"), "expenditure": Decimal("6000.00")},
            {"restaurant": restaurants["Speedy Burger 365"], "income": Decimal("25000.00"), "expenditure": Decimal("18000.00")},
            {"restaurant": restaurants["Speedy Burger 365"], "income": Decimal("6000.00"), "expenditure": Decimal("9000.00")},
        ]

        created_sales = [Sale.objects.create(**s) for s in sales_data]
        self.stdout.write(self.style.SUCCESS(f"Created {len(created_sales)} sale records successfully!"))
