from celery import shared_task
from django.utils import timezone
from .models import Brand

@shared_task
def reset_daily_spend_task():
    today = timezone.now()
    if today.hour == 0:
        brands = Brand.objects.all()
        for brand in brands:
            brand.reset_daily_spent()

@shared_task
def reset_monthly_spend_task():
    today = timezone.now()
    if today.day == 1:
        brands = Brand.objects.all()
        for brand in brands:
            brand.reset_monthly_spent()
