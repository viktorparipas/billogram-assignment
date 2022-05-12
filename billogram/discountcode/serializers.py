from django.utils.timezone import now
from rest_framework import exceptions

from billogram.discountcode import models
from billogram.framework import MyModelSerializer


class DiscountCodeSerializer(MyModelSerializer):
    class Meta:
        model = models.DiscountCode
        fields = (
            'id',
            'rule',
            'valid_until',
        )

    def validate_rule(self, rule):
        user = self.get_user()
        if (user and not user.is_brand) or (user and user.brand != rule.brand):
            raise exceptions.ValidationError(
                "The discount code must belong to the same brand as the initiating request")
        else:
            return rule


class DiscountRuleSerializer(MyModelSerializer):
    class Meta:
        model = models.DiscountRule
        fields = (
            'id',
            'brand',
            'discount',
        )
        read_only_fields = (
            'id',
            'brand',
            'discount',
        )


class DiscountCodeUsageSerializer(MyModelSerializer):
    class Meta:
        model = models.DiscountCodeUsage
        fields = (
            'discount_code',
            'user',
        )

    def validate_discount_code(self, code):
        # Here we could validate if the user is authorized to use discount code
        # In the current implementation every discount code is fair game for all users
        # But they are not exposed through the API
        # For now the validity date is checked
        if now().date() > code.valid_until:
            raise exceptions.ValidationError("Discount code must be valid at the time of use")
        else:
            return code

    def validate_user(self, user):
        serializing_user = self.get_user()
        if serializing_user.is_brand:
            raise exceptions.ValidationError("Brands cannot use discount codes")
        elif serializing_user != user:
            raise exceptions.ValidationError("Users cannot use discount codes in someone else's name")

        return user


class BrandSerializer(MyModelSerializer):
    class Meta:
        model = models.Brand
        fields = (
            'id',
            'name',
        )
