"""
AgriTech AI — Basic Unit Tests
Run with: python -m pytest tests/ -v
"""
import sys
import os

# Add parent directory to path so we can import project modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from core.auth_manager import create_user, login_user, init_auth_db, hash_password, check_password
from core.database import init_db, add_record, get_history
from engines.price_engine import get_predicted_price
from engines.satellite_engine import calculate_ndvi


# =============================================
# 1. AUTH MANAGER TESTS
# =============================================

class TestAuthManager:

    def test_hash_password_returns_bytes(self):
        """bcrypt hash should always return bytes."""
        hashed = hash_password("testpassword123")
        assert isinstance(hashed, bytes), "Hash must be bytes"

    def test_hash_is_not_plaintext(self):
        """The hash must not equal the plain password."""
        password = "mysecretpass"
        hashed = hash_password(password)
        assert hashed != password.encode(), "Password must not be stored in plain text!"

    def test_check_password_correct(self):
        """Correct password should verify successfully."""
        password = "correctpass"
        hashed = hash_password(password)
        assert check_password(password, hashed) is True

    def test_check_password_wrong(self):
        """Wrong password should fail verification."""
        hashed = hash_password("realpassword")
        assert check_password("wrongpassword", hashed) is False

    def test_two_hashes_of_same_password_differ(self):
        """bcrypt salting: same password → different hashes each time."""
        pw = "samepassword"
        h1 = hash_password(pw)
        h2 = hash_password(pw)
        assert h1 != h2, "Hashes of the same password must differ (bcrypt salt)"


# =============================================
# 2. NDVI CALCULATION TESTS
# =============================================

class TestNDVI:

    def test_ndvi_range_valid(self):
        """NDVI must always be between 0 and 1."""
        ndvi = calculate_ndvi(lat=20.5, lon=78.9, n=90, p=42, k=43, rainfall=50)
        assert 0.0 <= ndvi <= 1.0, f"NDVI out of range: {ndvi}"

    def test_ndvi_higher_with_good_nutrients(self):
        """High N, P, K should produce higher NDVI than low nutrients."""
        ndvi_high = calculate_ndvi(lat=20.0, lon=78.0, n=200, p=200, k=200, rainfall=100)
        ndvi_low  = calculate_ndvi(lat=20.0, lon=78.0, n=10,  p=10,  k=10,  rainfall=10)
        assert ndvi_high > ndvi_low, "Richer nutrients should yield higher NDVI"

    def test_ndvi_zero_rainfall_is_lower(self):
        """Zero rainfall should produce lower NDVI than moderate rainfall."""
        ndvi_dry  = calculate_ndvi(lat=25.0, lon=80.0, n=90, p=42, k=43, rainfall=0)
        ndvi_good = calculate_ndvi(lat=25.0, lon=80.0, n=90, p=42, k=43, rainfall=120)
        assert ndvi_dry < ndvi_good, "Drought conditions should reduce NDVI"

    def test_ndvi_never_exceeds_095(self):
        """NDVI is capped at 0.95 (perfect conditions are rare)."""
        ndvi = calculate_ndvi(lat=10.0, lon=75.0, n=250, p=250, k=250, rainfall=150)
        assert ndvi <= 0.95, f"NDVI should not exceed 0.95, got {ndvi}"


# =============================================
# 3. DATABASE TESTS
# =============================================

class TestDatabase:

    def test_init_db_creates_table(self):
        """init_db() should run without raising exceptions."""
        try:
            init_db()
        except Exception as e:
            pytest.fail(f"init_db() raised an exception: {e}")

    def test_add_and_retrieve_record(self):
        """A record added should be retrievable from history."""
        init_db()
        initial_count = len(get_history())
        add_record("TestCity", 90, 42, 43, 6.5, 80, "rice", 15000.0)
        new_count = len(get_history())
        assert new_count == initial_count + 1, "Record count should increase by 1 after add"

    def test_history_returns_dataframe(self):
        """get_history() should always return a pandas DataFrame."""
        import pandas as pd
        init_db()
        result = get_history()
        assert isinstance(result, pd.DataFrame), "get_history() must return a DataFrame"


# =============================================
# 4. PRICE ENGINE TESTS
# =============================================

class TestPriceEngine:

    def test_price_returns_float(self):
        """Price prediction should return a float value."""
        result = get_predicted_price("rice", 90, 42, 43, 6.5, 80, 5)
        assert isinstance(result, float), f"Expected float, got {type(result)}"

    def test_price_non_negative(self):
        """Predicted price should never be negative."""
        result = get_predicted_price("wheat", 60, 55, 44, 7.0, 50, 10)
        assert result >= 0.0, f"Price should be non-negative, got {result}"

    def test_price_returns_zero_on_bad_model(self):
        """If model file doesn't exist, should return 0.0 gracefully (no crash)."""
        import joblib
        original_load = joblib.load

        def mock_load(_path):
            raise FileNotFoundError("mock: model not found")

        joblib.load = mock_load
        try:
            result = get_predicted_price("cotton", 90, 42, 43, 6.5, 80, 5)
            assert result == 0.0, "Should return 0.0 when model file is missing"
        finally:
            joblib.load = original_load


# =============================================
# Run directly: python tests/test_basic.py
# =============================================
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
