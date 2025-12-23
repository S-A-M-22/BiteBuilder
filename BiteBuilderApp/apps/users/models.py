from django.db import models

class Profile(models.Model):
    id = models.UUIDField(primary_key=True)
    username = models.CharField(max_length=32, unique=True)
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)

    class Meta:
        db_table = "users_profile"
