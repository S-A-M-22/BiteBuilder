import uuid
from django.db import models
from .goal import Goal
from .nutrients import Nutrient


import uuid
from django.db import models
from .goal import Goal
from .nutrients import Nutrient


class GoalNutrient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    goal = models.ForeignKey(
        Goal,
        on_delete=models.CASCADE,
        db_column="goal_id",
        related_name="goal_nutrients",
    )

    nutrient = models.ForeignKey(
        Nutrient,
        on_delete=models.CASCADE,
        db_column="nutrient_id",
        related_name="nutrient_goals",
    )

    target_amount = models.FloatField(help_text="Target amount per period (unit of nutrient)")
    consumed_amount = models.FloatField(default=0, help_text="Consumed amount so far in same unit")

    class Meta:
        db_table = "bitebuilder.goal_nutrient"
        unique_together = ("goal", "nutrient")
        indexes = [
            models.Index(fields=["goal"]),
            models.Index(fields=["nutrient"]),
        ]

    def __str__(self):
        return f"{self.goal_id} → {self.nutrient_id}: {self.consumed_amount}/{self.target_amount}"

    @property
    def progress_percent(self):
        if not self.target_amount:
            return 0
        return round(min(self.consumed_amount / self.target_amount * 100, 100), 1)
