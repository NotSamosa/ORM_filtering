from datetime import timedelta
from decimal import Decimal
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone
from restaurants import queries as q
from restaurants.models import Restaurant, Sale


class QFilterQueryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        today = timezone.now().date()

        cls.r_italian_recent = Restaurant.objects.create(
            name="Luigi's Italian Grill",
            restaurant_type=Restaurant.RestaurantType.ITALIAN,
            date_opened=today - timedelta(days=10),
        )
        cls.r_mexican_old = Restaurant.objects.create(
            name="Taco Fiesta 24",
            restaurant_type=Restaurant.RestaurantType.MEXICAN,
            date_opened=today - timedelta(days=45),
        )
        cls.r_american_recent = Restaurant.objects.create(
            name="Downtown Smokehouse & GRILL",
            restaurant_type=Restaurant.RestaurantType.AMERICAN,
            date_opened=today - timedelta(days=15),
        )
        cls.r_italian_old_cafe = Restaurant.objects.create(
            name="Bella Roma Cafe",
            restaurant_type=Restaurant.RestaurantType.ITALIAN,
            date_opened=today - timedelta(days=90),
        )
        cls.r_french_old = Restaurant.objects.create(
            name="Cafe Royale",
            restaurant_type=Restaurant.RestaurantType.FRENCH,
            date_opened=today - timedelta(days=200),
        )

        Sale.objects.create(
            restaurant=cls.r_italian_recent,
            income=Decimal("15000.00"),
            expenditure=Decimal("9000.00"),
        )
        Sale.objects.create(
            restaurant=cls.r_mexican_old,
            income=Decimal("4000.00"),
            expenditure=Decimal("6000.00"),
        )
        Sale.objects.create(
            restaurant=cls.r_italian_old_cafe,
            income=Decimal("3000.00"),
            expenditure=Decimal("5000.00"),
        )

    def test_italian_or_mexican_query(self):
        qs = q.get_italian_or_mexican_restaurants()
        names = set(qs.values_list("name", flat=True))
        self.assertEqual(
            names,
            {"Luigi's Italian Grill", "Taco Fiesta 24", "Bella Roma Cafe"},
        )

    def test_not_recently_opened_query(self):
        qs = q.get_not_recently_opened_restaurants()
        names = set(qs.values_list("name", flat=True))
        self.assertEqual(
            names,
            {"Taco Fiesta 24", "Bella Roma Cafe", "Cafe Royale"},
        )

    def test_type_or_recently_opened_query(self):
        qs = q.get_italian_mexican_or_recently_opened_restaurants()
        names = set(qs.values_list("name", flat=True))
        self.assertIn("Luigi's Italian Grill", names)
        self.assertIn("Taco Fiesta 24", names)
        self.assertIn("Downtown Smokehouse & GRILL", names)
        self.assertIn("Bella Roma Cafe", names)
        self.assertNotIn("Cafe Royale", names)

    def test_contains_grill_case_insensitive(self):
        qs = q.get_restaurants_containing_grill()
        names = set(qs.values_list("name", flat=True))
        self.assertEqual(
            names,
            {"Luigi's Italian Grill", "Downtown Smokehouse & GRILL"},
        )

    def test_ends_with_cafe(self):
        qs = q.get_restaurants_ending_with_cafe()
        names = list(qs.values_list("name", flat=True))
        self.assertEqual(names, ["Bella Roma Cafe"])
        self.assertNotIn("Cafe Royale", names)

    def test_name_contains_digits_regex(self):
        qs = q.get_restaurants_with_digits()
        names = list(qs.values_list("name", flat=True))
        self.assertEqual(names, ["Taco Fiesta 24"])

    def test_sales_profitable_or_restaurant_has_digit(self):
        qs = q.get_sales_profitable_or_restaurant_has_digit()
        self.assertEqual(qs.count(), 2)

    def test_select_related_performance(self):
        with self.assertNumQueries(1):
            sales = list(q.get_sales_profitable_or_restaurant_has_digit())
            _ = [s.restaurant.name for s in sales]

    @override_settings(DEBUG=True)
    def test_management_commands_execution(self):
        call_command("seed_data")
        call_command("q_filter_demo")
