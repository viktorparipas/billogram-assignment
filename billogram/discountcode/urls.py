from django.urls import re_path
from rest_framework import routers

from billogram.discountcode import views

router = routers.SimpleRouter()
router.register(r'discountcode', views.DiscountCodeViewSet, 'code')
router.register(r'discountcodeusage', views.DiscountCodeUsageViewSet, 'usage')

urlpatterns = router.urls + [
    re_path(r'^docs(?P<format>\.json|\.yaml)$', views.schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^docs/?$', views.schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]