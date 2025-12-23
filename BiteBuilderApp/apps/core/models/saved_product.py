# apps/core/models/saved_product.py
import uuid
from django.db import models
from apps.users.models import Profile
from .product import Product


class SavedProduct(models.Model):
    """
    Represents a user saving a global product (bookmark/collection).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="saved_products",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="saved_by_users",
    )
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bitebuilder.saved_product"
        unique_together = ("user", "product")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self):
        return f"{self.user.username} saved {self.product.name}"
