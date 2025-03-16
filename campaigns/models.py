from django.db import models
from django.utils import timezone
from enum import Enum

class SPEND_STATUS(Enum):
    COMPLETED = 1
    DAILY_BUDGET_SPENT = 2
    MONTHLY_BUDGET_SPENT = 3
    OUT_OF_DAYPARTING = 4

class Brand(models.Model):
    name = models.CharField(max_length=255)
    monthly_budget = models.DecimalField(max_digits=10, decimal_places=2)
    daily_budget = models.DecimalField(max_digits=10, decimal_places=2)
    current_monthly_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    current_daily_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def reset_daily_spent(self):
        self.current_daily_spent = 0.0
        self.check_spends()
        self.save()

    def reset_monthly_spent(self):
        self.current_monthly_spent = 0.0
        self.check_spends()
        self.save()

    def check_spends(self):
        if not self.is_daily_budget_spent() and not self.is_monthly_budget_spent():
            self.campaigns.update(active=True)
        else:
            self.campaigns.update(active=False)

    def is_daily_budget_spent(self):
        return self.current_daily_spent >= self.daily_budget

    def is_monthly_budget_spent(self):
        return self.current_monthly_spent >= self.monthly_budget
    
    def get_spend_status(self):
        if self.is_daily_budget_spent():
            return SPEND_STATUS.DAILY_BUDGET_SPENT
        elif self.is_monthly_budget_spent():
            return SPEND_STATUS.MONTHLY_BUDGET_SPENT
        else:
            return SPEND_STATUS.OUT_OF_DAYPARTING
    
    def __str__(self):
        return self.name

class Campaign(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="campaigns")
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    dayparting_start = models.TimeField(null=True, blank=True)
    dayparting_end = models.TimeField(null=True, blank=True)

    def spend(self, amount):
        if self.active and self.dayparting_ok():
            self.brand.current_daily_spent += amount
            self.brand.current_monthly_spent += amount
            self.brand.check_spends()
            self.brand.save()
            return SPEND_STATUS.COMPLETED
        
        return self.brand.get_spend_status()

    def dayparting_ok(self):
        now = timezone.now()
        start = self.dayparting_start
        end = self.dayparting_end
        
        if start is not None and now.time() < start:
            return False
        elif end is not None and now.time() > end:
            return False
        
        return True

    def __str__(self):
        return self.name
