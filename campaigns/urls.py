from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BrandViewSet, CampaignViewSet, SpendAPIViewSet

router = DefaultRouter()
router.register(r'brands', BrandViewSet)
router.register(r'campaigns', CampaignViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('campaigns/<int:campaign_id>/spend/', SpendAPIViewSet.as_view(), name='campaign-spend'),
]
