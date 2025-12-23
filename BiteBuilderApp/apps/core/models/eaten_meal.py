import uuid
from django.db import models
from django.utils import timezone
from ...users.models import Profile
from .meal import Meal


class EatenMeal(models.Model):
    """
    Represents a single instance of a meal being eaten by a user.
    Links back to the Meal template for composition.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="eaten_meals",
        db_column="user_id",
    )
    meal = models.ForeignKey(
        Meal,
        on_delete=models.CASCADE,
        related_name="eaten_instances",
        db_column="meal_id",
    )
    eaten_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "bitebuilder.eaten_meal"
        indexes = [
            models.Index(fields=["user", "eaten_at"]),
        ]

    def __str__(self):
        return f"{self.user_id} ate {self.meal_id} at {self.eaten_at:%Y-%m-%d %H:%M}"
