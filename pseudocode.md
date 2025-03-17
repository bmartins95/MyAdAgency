# Brand class:

Brand:

- name: String
- monthly_budget: Decimal
- daily_budget: Decimal
- current_monthly_spent: Decimal
- current_daily_spent: Decimal

# Campaign class:

Campaign:

- brand: Brand
- name: String
- active: Boolean
- dayparting_start: Time
- dayparting_end: Time

# Pseudo-code

```
Function reset_daily_spent(brand):
  brand.current_daily_spent = 0
  brand.check_spends()
  brand.save()

Function reset_monthly_spent(brand):
  brand.current_monthly_spent = 0
  brand.check_spends()
  brand.save()

Function check_spends(brand):
  If brand.is_daily_budget_spent() OR brand.is_monthly_budget_spent():
    Deactivate all campaigns in brand
  Else:
    Activate all campaigns in brand
  brand.save()

Function is_daily_budget_spent(brand):
  Return brand.current_daily_spent >= brand.daily_budget

Function is_monthly_budget_spent(brand):
  Return brand.current_monthly_spent >= brand.monthly_budget

Function spend(campaign, amount):
  If campaign.active AND campaign.dayparting_ok():
    Increase brand's current_daily_spent by amount
    Increase brand's current_monthly_spent by amount
    brand.check_spends()
    brand.save()
    Return SPEND_STATUS.COMPLETED
  Else:
    Return brand.get_spend_status()

Function dayparting_ok(campaign):
  current_time = get_current_time()
  If campaign.dayparting_start is not None AND current_time < campaign.dayparting_start:
    Return False
  If campaign.dayparting_end is not None AND current_time > campaign.dayparting_end:
    Return False
  Return True
```
