from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, time, timezone as date_timezone
from mock import patch

from .models import Brand, Campaign


class BrandModelTest(TestCase):

    def setUp(self):
        self.brand = Brand.objects.create(
            name = "Test Brand",
            monthly_budget = Decimal('1000.00'),
            daily_budget = Decimal('100.00')
        )

    def test_reset_daily_spent(self):
        self.brand.current_daily_spent = Decimal('50.00')
        self.brand.save()
        self.assertEqual(self.brand.current_daily_spent, Decimal('50.00'))

        self.brand.reset_daily_spent()

        self.assertEqual(self.brand.current_daily_spent, Decimal('0.00'))

    def test_reset_monthly_spent(self):
        self.brand.current_monthly_spent = Decimal('500.00')
        self.brand.save()
        self.assertEqual(self.brand.current_monthly_spent, Decimal('500.00'))

        self.brand.reset_monthly_spent()

        self.assertEqual(self.brand.current_monthly_spent, Decimal('0.00'))

    def test_is_daily_budget_spent(self):
        self.brand.current_daily_spent = Decimal('100.00')
        self.brand.save()
        
        self.assertTrue(self.brand.is_daily_budget_spent())

        self.brand.current_daily_spent = Decimal('50.00')
        self.brand.save()

        self.assertFalse(self.brand.is_daily_budget_spent())

    def test_is_monthly_budget_spent(self):
        self.brand.current_monthly_spent = Decimal('1000.00')
        self.brand.save()

        self.assertTrue(self.brand.is_monthly_budget_spent())

        self.brand.current_monthly_spent = Decimal('500.00')
        self.brand.save()

        self.assertFalse(self.brand.is_monthly_budget_spent())

    def test_campaign_inactive_after_spent(self):
        campaign1 = Campaign.objects.create(brand=self.brand, name="Campaign 1")
        campaign2 = Campaign.objects.create(brand=self.brand, name="Campaign 2")

        self.assertTrue(campaign1.active)
        self.assertTrue(campaign2.active)

        self.brand.current_daily_spent = Decimal('150.00')
        self.brand.save()

        self.brand.check_spends()
        campaign1.refresh_from_db()
        campaign2.refresh_from_db()

        self.assertFalse(campaign1.active)
        self.assertFalse(campaign2.active)

    def test_campaign_active_after_spent_reset(self):
        campaign1 = Campaign.objects.create(brand=self.brand, name="Campaign 1")
        campaign2 = Campaign.objects.create(brand=self.brand, name="Campaign 2")

        self.brand.current_daily_spent = Decimal('150.00')
        self.brand.save()

        self.brand.check_spends()
        campaign1.refresh_from_db()
        campaign2.refresh_from_db()

        self.assertFalse(campaign1.active)
        self.assertFalse(campaign2.active)

        self.brand.reset_daily_spent()
        campaign1.refresh_from_db()
        campaign2.refresh_from_db()

        self.assertTrue(campaign1.active)
        self.assertTrue(campaign2.active)


    def test_str_method(self):
        """Test the __str__ method."""
        self.assertEqual(str(self.brand), "Test Brand")

class CampaignModelTest(TestCase):

    def setUp(self):
        self.brand = Brand.objects.create(
            name="Test Brand",
            monthly_budget = Decimal('1000.00'),
            daily_budget = Decimal('100.00'),
        )
        self.campaign = Campaign.objects.create(
            brand=self.brand, 
            name="Test Campaign",
            dayparting_start = time(9, 0),
            dayparting_end = time(17, 0),
        )

    def test_spend_method_with_active_campaign(self):
        dt = datetime(2025, 3, 16, 10, 0, tzinfo = date_timezone.utc)
        with patch.object(timezone, 'now', return_value=dt):
            self.campaign.spend(Decimal('10.00'))

            self.assertEqual(self.brand.current_daily_spent, Decimal('10.00'))
            self.assertEqual(self.brand.current_monthly_spent, Decimal('10.00'))

    def test_spend_method_with_inactive_campaign(self):
        dt = datetime(2025, 3, 16, 10, 0, tzinfo = date_timezone.utc)
        with patch.object(timezone, 'now', return_value=dt):
            self.campaign.active = False
            self.campaign.save()

            self.campaign.spend(Decimal('10.00'))

            self.assertEqual(self.brand.current_daily_spent, Decimal('0.00'))
            self.assertEqual(self.brand.current_monthly_spent, Decimal('0.00'))

    def test_campaign_inactive_after_budget_spent(self):
        dt = datetime(2025, 3, 16, 10, 0, tzinfo = date_timezone.utc)
        with patch.object(timezone, 'now', return_value=dt):
            self.assertTrue(self.campaign.active)

            self.campaign.spend(Decimal('100.00'))

            self.campaign.refresh_from_db()

            self.assertEqual(self.brand.current_daily_spent, Decimal('100.00'))
            self.assertEqual(self.brand.current_monthly_spent, Decimal('100.00'))
            self.assertFalse(self.campaign.active)

    def test_dayparting_ok(self):
        with self.subTest("Within time range"):
            dt = datetime(2025, 3, 16, 10, 0, tzinfo = date_timezone.utc)
            with patch.object(timezone, 'now', return_value=dt):
                self.assertTrue(self.campaign.dayparting_ok())

        with self.subTest("Before start time"):
            dt = datetime(2025, 3, 16, 8, 0, tzinfo = date_timezone.utc)
            with patch.object(timezone, 'now', return_value=dt):
                self.assertFalse(self.campaign.dayparting_ok())

        with self.subTest("After end time"):
            dt = datetime(2025, 3, 16, 18, 0, tzinfo = date_timezone.utc)
            with patch.object(timezone, 'now', return_value=dt):
                self.assertFalse(self.campaign.dayparting_ok())

        with self.subTest("No dayparting set"):
            self.campaign.dayparting_start = None
            self.campaign.dayparting_end = None
            self.assertTrue(self.campaign.dayparting_ok())

    def test_str_method(self):
        """Test the __str__ method."""
        self.assertEqual(str(self.campaign), "Test Campaign")
