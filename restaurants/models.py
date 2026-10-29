from django.db import models


class Restaurant(models.Model):
    class RestaurantType(models.TextChoices):
        ITALIAN = 'Italian', 'Italian'
        MEXICAN = 'Mexican', 'Mexican'
        CHINESE = 'Chinese', 'Chinese'
        AMERICAN = 'American', 'American'
        INDIAN = 'Indian', 'Indian'
        FRENCH = 'French', 'French'
        FAST_FOOD = 'Fast Food', 'Fast Food'

    name = models.CharField(max_length=150)
    restaurant_type = models.CharField(
        max_length=50,
        choices=RestaurantType.choices,
        default=RestaurantType.ITALIAN,
    )
    date_opened = models.DateField()

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.name} ({self.restaurant_type})"


class Sale(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='sales',
    )
    income = models.DecimalField(max_digits=12, decimal_places=2)
    expenditure = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"Sale #{self.id} for {self.restaurant.name} (Income: {self.income}, Exp: {self.expenditure})"
