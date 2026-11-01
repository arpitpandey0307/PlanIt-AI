"""Tests for configuration and decision rules."""
import pytest
from app.config import DecisionRules, BUDGET_PROFILES, VENDOR_CATEGORIES, get_settings


class TestCityTier:
    """Tests for city tier classification."""

    def test_mumbai_is_tier1(self):
        assert DecisionRules.get_city_tier("Mumbai") == "tier1"

    def test_delhi_is_tier1(self):
        assert DecisionRules.get_city_tier("Delhi") == "tier1"

    def test_bangalore_is_tier1(self):
        assert DecisionRules.get_city_tier("Bangalore") == "tier1"

    def test_hyderabad_is_tier1(self):
        assert DecisionRules.get_city_tier("Hyderabad") == "tier1"

    def test_jaipur_is_tier2(self):
        assert DecisionRules.get_city_tier("Jaipur") == "tier2"

    def test_ahmedabad_is_tier2(self):
        assert DecisionRules.get_city_tier("Ahmedabad") == "tier2"

    def test_unknown_city_is_tier3(self):
        assert DecisionRules.get_city_tier("Udaipur") == "tier3"

    def test_case_insensitive(self):
        assert DecisionRules.get_city_tier("MUMBAI") == "tier1"
        assert DecisionRules.get_city_tier("mumbai") == "tier1"


class TestPeakSeason:
    """Tests for peak season detection."""

    def test_wedding_october_is_peak(self):
        assert DecisionRules.is_peak_season("wedding", 10) is True

    def test_wedding_november_is_peak(self):
        assert DecisionRules.is_peak_season("wedding", 11) is True

    def test_wedding_february_is_peak(self):
        assert DecisionRules.is_peak_season("wedding", 2) is True

    def test_wedding_july_is_not_peak(self):
        assert DecisionRules.is_peak_season("wedding", 7) is False

    def test_birthday_may_is_peak(self):
        assert DecisionRules.is_peak_season("birthday", 5) is True

    def test_birthday_december_is_peak(self):
        assert DecisionRules.is_peak_season("birthday", 12) is True

    def test_birthday_march_is_not_peak(self):
        assert DecisionRules.is_peak_season("birthday", 3) is False

    def test_community_october_is_peak(self):
        assert DecisionRules.is_peak_season("community", 10) is True

    def test_community_january_is_not_peak(self):
        assert DecisionRules.is_peak_season("community", 1) is False


class TestBudgetProfilesConfig:
    """Tests for budget profile configuration validity."""

    def test_all_profiles_sum_to_100(self):
        for name, profile in BUDGET_PROFILES.items():
            total = sum(profile.values())
            assert abs(total - 100.0) < 0.01, f"{name} sums to {total}"

    def test_all_values_positive(self):
        for name, profile in BUDGET_PROFILES.items():
            for category, value in profile.items():
                assert value > 0, f"{name}.{category} is {value}"

    def test_wedding_profile_exists(self):
        assert "wedding" in BUDGET_PROFILES

    def test_birthday_profile_exists(self):
        assert "birthday" in BUDGET_PROFILES

    def test_community_profile_exists(self):
        assert "community" in BUDGET_PROFILES


class TestVendorCategories:
    """Tests for vendor category configuration."""

    def test_wedding_vendors_exist(self):
        assert "wedding" in VENDOR_CATEGORIES
        assert len(VENDOR_CATEGORIES["wedding"]) > 0

    def test_birthday_vendors_exist(self):
        assert "birthday" in VENDOR_CATEGORIES
        assert len(VENDOR_CATEGORIES["birthday"]) > 0

    def test_community_vendors_exist(self):
        assert "community" in VENDOR_CATEGORIES
        assert len(VENDOR_CATEGORIES["community"]) > 0

    def test_vendor_templates_have_required_fields(self):
        for event_type, vendors in VENDOR_CATEGORIES.items():
            for vendor in vendors:
                assert "name" in vendor, f"{event_type} vendor missing 'name'"
                assert "lead_time_weeks" in vendor
                assert "questions" in vendor
                assert "diligence" in vendor
                assert len(vendor["questions"]) > 0
                assert len(vendor["diligence"]) > 0


class TestDecisionRulesConstants:
    """Tests for decision rules constants."""

    def test_standard_planning_weeks(self):
        assert DecisionRules.STANDARD_PLANNING_WEEKS == 12

    def test_short_notice_days(self):
        assert DecisionRules.SHORT_NOTICE_DAYS == 14

    def test_large_event_threshold(self):
        assert DecisionRules.LARGE_EVENT_THRESHOLD == 200

    def test_min_per_guest_cost_exists(self):
        assert "wedding" in DecisionRules.MIN_PER_GUEST_COST
        assert "birthday" in DecisionRules.MIN_PER_GUEST_COST
        assert "community" in DecisionRules.MIN_PER_GUEST_COST


class TestSettings:
    """Tests for application settings."""

    def test_settings_loads(self):
        settings = get_settings()
        assert settings is not None

    def test_settings_defaults(self):
        settings = get_settings()
        assert settings.port == 8000
        assert settings.model_name == "gemini-1.5-flash"
        assert settings.max_tokens == 2048

