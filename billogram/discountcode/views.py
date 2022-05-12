
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from markdown_deux import markdown
from rest_framework import permissions
from rest_framework.viewsets import ReadOnlyModelViewSet

from billogram import settings
from billogram.discountcode import models, serializers
from billogram.framework import CreateModelMixInWithObjectPermissionCheck, ViewMixIn


description = """
Discount code service API documentation
"""
schema_view = get_schema_view(
    openapi.Info(
        title="Discount code service",
        default_version='v1',
        description=markdown(description),
        contact=openapi.Contact(email='viktorparipas@gmail.com'),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url="http://localhost:8000",
)


class DiscountCodeViewSet(CreateModelMixInWithObjectPermissionCheck, ViewMixIn, ReadOnlyModelViewSet):
    serializer_class = serializers.DiscountCodeSerializer

    def get_queryset(self):
        if self.request.user and self.request.user.is_staff:
            return models.DiscountCode.objects.all()
        elif self.request.user and self.request.user.is_brand:
            return models.DiscountCode.objects.filter(rule__brand=self.request.user.brand)
        else:
            return models.DiscountCode.objects.none()


class DiscountRuleViewSet(
        CreateModelMixInWithObjectPermissionCheck,
        ViewMixIn,
        ReadOnlyModelViewSet
):
    serializer_class = serializers.DiscountRuleSerializer

    def get_queryset(self):
        if self.request.user and self.request.user.is_staff:
            return models.DiscountRule.objects.all()
        elif self.request.user and self.request.user.is_brand:
            return models.DiscountRule.objects.filter(brand=self.request.user.brand)
        else:
            return models.DiscountRule.objects.none()


class DiscountCodeUsageViewSet(CreateModelMixInWithObjectPermissionCheck, ViewMixIn, ReadOnlyModelViewSet):
    serializer_class = serializers.DiscountCodeUsageSerializer

    def get_queryset(self):
        if self.request.user and self.request.user.is_staff:
            return models.DiscountCodeUsage.objects.all()
        elif self.request.user and self.request.user.is_brand:
            return models.DiscountCodeUsage.objects.filter(discount_code__rule__brand=self.request.user.brand)
        else:
            return models.DiscountCodeUsage.objects.filter(user=self.request.user)
