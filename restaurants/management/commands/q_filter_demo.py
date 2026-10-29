from django.core.management.base import BaseCommand
from django.db import connection, reset_queries
from restaurants.models import Restaurant, Sale
from restaurants import queries as q


class Command(BaseCommand):
    help = "Demonstrates advanced Django Q objects, pattern matching, and regex lookups"

    def print_query_section(self, section_id, title, q_repr, queryset, display_attr=None):
        self.stdout.write(self.style.MIGRATE_HEADING(f"\n[{section_id}] {title}"))
        self.stdout.write(f"  Q Expression : {q_repr}")

        reset_queries()
        results = list(queryset)
        sql = connection.queries[-1]["sql"] if connection.queries else str(queryset.query)

        self.stdout.write(f"  Result Count : {len(results)}")
        self.stdout.write("  Matches      :")
        if not results:
            self.stdout.write("    (No records matched)")
        else:
            for item in results:
                if display_attr:
                    val = display_attr(item)
                else:
                    val = str(item)
                self.stdout.write(f"    - {val}")

        self.stdout.write("  Generated SQL:")
        self.stdout.write(f"    {sql}")

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=" * 80))
        self.stdout.write(self.style.SUCCESS(" DJANGO ORM Q OBJECTS & ADVANCED LOOKUPS DEMONSTRATION"))
        self.stdout.write(self.style.SUCCESS("=" * 80))

        # 1a
        self.print_query_section(
            "1a",
            "Restaurants where restaurant_type is Italian OR Mexican",
            "Q(restaurant_type='Italian') | Q(restaurant_type='Mexican')",
            q.get_italian_or_mexican_restaurants(),
            lambda r: f"{r.name} (Type: {r.restaurant_type})",
        )

        # 1b
        self.print_query_section(
            "1b",
            "Restaurants NOT opened in the last 30 days (Negation)",
            "~Q(date_opened__gte=thirty_days_ago)",
            q.get_not_recently_opened_restaurants(),
            lambda r: f"{r.name} (Opened: {r.date_opened})",
        )

        # 1c
        self.print_query_section(
            "1c",
            "Combined: Italian/Mexican OR opened in last 30 days",
            "italian_mexican_q | recently_opened_q",
            q.get_italian_mexican_or_recently_opened_restaurants(),
            lambda r: f"{r.name} (Type: {r.restaurant_type}, Opened: {r.date_opened})",
        )

        # 2a
        self.print_query_section(
            "2a",
            "Restaurants whose name contains 'grill' (case-insensitive)",
            "Q(name__icontains='grill')",
            q.get_restaurants_containing_grill(),
            lambda r: f"{r.name}",
        )

        # 2b
        self.print_query_section(
            "2b",
            "Restaurants whose name ends with 'Cafe'",
            "Q(name__endswith='Cafe')",
            q.get_restaurants_ending_with_cafe(),
            lambda r: f"{r.name}",
        )

        # 3a
        self.print_query_section(
            "3a",
            "Restaurants whose name contains one or more digits (Regex)",
            r"Q(name__regex=r'\d+')",
            q.get_restaurants_with_digits(),
            lambda r: f"{r.name}",
        )

        # 3b
        self.print_query_section(
            "3b",
            "Sales where income > expenditure OR restaurant name contains digits",
            r"Q(income__gt=F('expenditure')) | Q(restaurant__name__regex=r'\d+')",
            q.get_sales_profitable_or_restaurant_has_digit(),
            lambda s: (
                f"Sale #{s.id} | Restaurant: '{s.restaurant.name}' | "
                f"Income: ${s.income} | Exp: ${s.expenditure} | "
                f"Profitable: {s.income > s.expenditure}"
            ),
        )

        # 4: Composed query
        self.print_query_section(
            "4",
            "Composed Sale Query (Italian/Mexican OR Digit-in-name) AND Profitable",
            "(Q(restaurant__type__in=['Italian', 'Mexican']) | Q(restaurant__name__regex=r'\\d+')) & profitable_q",
            q.get_composed_sales(),
            lambda s: (
                f"Sale #{s.id} | Restaurant: '{s.restaurant.name}' ({s.restaurant.restaurant_type}) | "
                f"Income: ${s.income} | Exp: ${s.expenditure}"
            ),
        )

        # 5: Performance Optimization (select_related)
        self.stdout.write(self.style.MIGRATE_HEADING("\n[5] Performance Optimization Demonstration: select_related('restaurant')"))

        # Without select_related
        reset_queries()
        unoptimized_sales = list(Sale.objects.filter(q.sale_profitable_or_digit_restaurant_q))
        _ = [s.restaurant.name for s in unoptimized_sales]
        unoptimized_query_count = len(connection.queries)

        # With select_related
        reset_queries()
        optimized_sales = list(Sale.objects.select_related('restaurant').filter(q.sale_profitable_or_digit_restaurant_q))
        _ = [s.restaurant.name for s in optimized_sales]
        optimized_query_count = len(connection.queries)

        self.stdout.write(f"  Sales evaluated           : {len(optimized_sales)}")
        self.stdout.write(f"  Query count WITHOUT select_related : {unoptimized_query_count} queries (N+1 query issue)")
        self.stdout.write(f"  Query count WITH select_related    : {optimized_query_count} query (Optimized SQL JOIN)")

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 80))
        self.stdout.write(self.style.SUCCESS(" DEMONSTRATION COMPLETE - ALL QUERIES EXECUTED SUCCESSFULLY"))
        self.stdout.write(self.style.SUCCESS("=" * 80 + "\n"))

