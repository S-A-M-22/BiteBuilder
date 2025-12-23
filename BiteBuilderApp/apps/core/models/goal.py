import uuid
from django.db import models
from ...users.models import Profile


class Goal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name="goal",
        db_column="user_id",
    )
    target_weight_kg = models.FloatField(null=True, blank=True)
    target_calories = models.IntegerField(null=True, blank=True)
    consumed_calories = models.FloatField(default=0)

    class ResetFrequency(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        NONE = "none", "No automatic reset"

    reset_frequency = models.CharField(
        max_length=10,
        choices=ResetFrequency.choices,
        default=ResetFrequency.NONE,
    )

    class Meta:
        db_table = "bitebuilder.goal"

    def __str__(self):
        return f"{self.user_id} • reset={self.reset_frequency}"
