from django.contrib.auth.models import AbstractUser, User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.timezone import now

from billogram.framework import MyModel


class MyUser(AbstractUser):
    is_brand = models.BooleanField(default=False)
    brand = models.ForeignKey('Brand', blank=True, null=True, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.is_brand and self.brand is None:
            self.is_brand = False

        return super().save(*args, **kwargs)

    def can_read(self, user):
        return True

    def can_update(self, user):
        return self == user

    def can_delete(self, user):
        return user.is_staff

    def can_create(self, user):
        return user.is_staff


class DiscountCode(MyModel):
    id = models.CharField(max_length=64, primary_key=True)
    rule = models.ForeignKey('DiscountRule', on_delete=models.CASCADE)
    valid_until = models.DateField(default=now().date())

    def __str__(self):
        return f"{self.id} until {self.valid_until}"

    # No discount codes are listed, but the user can fetch them by the ID
    # if they are aware of the ID
    def can_read(self, user):
        return True

    def can_create(self, user):
        if user.is_staff or user.is_brand:
            return True
        else:
            return False


class DiscountRule(MyModel):
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE)
    discount = models.IntegerField(validators=[MaxValueValidator(100), MinValueValidator(1)])

    def __str__(self):
        return f"{self.discount}% on {self.brand} products"


class DiscountCodeUsage(MyModel):
    id = models.CharField(max_length=255, blank=True, primary_key=True)
    discount_code = models.ForeignKey('DiscountCode', on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('discount_code', 'user')

    def __str__(self):
        return f"{self.id} at {self.used_at}"

    def save(self, *args, **kwargs):
        hashed_code = hash(self.discount_code.id)
        hashed_user_id = hash(self.user.id)
        _id = hash(hashed_code + hashed_user_id)
        self.id = _id
        return super().save(*args, **kwargs)

    def can_read(self, user):
        if user.is_staff:
            return True
        elif user.is_brand:
            return self.discount_code.rule.brand == user.brand
        else:
            return self.user == user

    def can_create(self, user):
        if user.is_staff or user.is_brand:
            return False
        else:
            return self.user == user


class Brand(MyModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
