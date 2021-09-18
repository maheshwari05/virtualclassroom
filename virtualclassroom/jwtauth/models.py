from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20)

    def __str__(self):
        return str(self.user) + "  ->  " + self.role