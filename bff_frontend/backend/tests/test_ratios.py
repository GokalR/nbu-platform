"""Tests for app.services.ratios — compute() financial ratios."""

import pytest

from app.services.ratios import compute, _safe_div


class TestSafeDiv:
    def test_normal_division(self):
        assert _safe_div(10.0, 5.0) == 2.0

    def test_returns_none_when_denominator_is_zero(self):
        assert _safe_div(10.0, 0) is None

    def test_returns_none_when_denominator_is_none(self):
        assert _safe_div(10.0, None) is None

    def test_returns_none_when_numerator_is_none(self):
        assert _safe_div(None, 5.0) is None

    def test_returns_none_when_both_none(self):
        assert _safe_div(None, None) is None


class TestCompute:
    def test_returns_empty_dicts_when_both_inputs_none(self):
        result = compute(None, None)
        assert "absolutes" in result
        assert "ratios" in result
        # All absolutes should be 0.0 (from g() fallback) or None
        # All ratios should be None (division by zero or None)
        for key, value in result["ratios"].items():
            assert value is None, f"ratio {key} should be None, got {value}"

    def test_computes_current_ratio_from_balance_data(self):
        form1 = {
            "390": 500_000.0,  # current_assets
            "600": 250_000.0,  # st_liab (current liabilities)
        }
        result = compute(form1, None)
        assert result["ratios"]["currentRatio"] == pytest.approx(2.0)

    def test_computes_net_profit_margin_from_pnl_data(self):
        form2 = {
            "010": 1_000_000.0,  # revenue
            "270": 200_000.0,    # net_profit
        }
        result = compute(None, form2)
        assert result["ratios"]["netMargin"] == pytest.approx(0.2)

    def test_computes_gross_margin(self):
        form2 = {
            "010": 1_000_000.0,  # revenue
            "030": 400_000.0,    # gross_profit
        }
        result = compute(None, form2)
        assert result["ratios"]["grossMargin"] == pytest.approx(0.4)

    def test_computes_roe(self):
        form1 = {"480": 500_000.0}   # equity
        form2 = {"270": 100_000.0}   # net_profit
        result = compute(form1, form2)
        assert result["ratios"]["roe"] == pytest.approx(0.2)

    def test_computes_debt_to_equity(self):
        form1 = {
            "480": 1_000_000.0,  # equity
            "570": 200_000.0,    # lt_bank_loans
            "730": 100_000.0,    # st_bank_loans
        }
        result = compute(form1, None)
        # total_debt = lt_bank_loans + (580 or 0) + st_bank_loans + (740 or 0) = 300_000
        assert result["ratios"]["debtToEquity"] == pytest.approx(0.3)

    def test_handles_missing_codes_gracefully(self):
        # Provide partial data — should not raise KeyError
        form1 = {"012": 100_000.0}
        form2 = {"010": 50_000.0}
        result = compute(form1, form2)
        assert isinstance(result, dict)
        assert "ratios" in result
        assert "absolutes" in result

    def test_absolutes_reflect_input_values(self):
        form1 = {
            "390": 500_000.0,
            "400": 1_000_000.0,
            "480": 600_000.0,
        }
        form2 = {
            "010": 800_000.0,
            "270": 120_000.0,
        }
        result = compute(form1, form2)
        assert result["absolutes"]["revenue"] == 800_000.0
        assert result["absolutes"]["totalAssets"] == 1_000_000.0
        assert result["absolutes"]["equity"] == 600_000.0
        assert result["absolutes"]["currentAssets"] == 500_000.0

    def test_net_profit_fallback_chain(self):
        # net_profit uses: form2["270"] or form2["260"] or form2["250"] or pretax_profit
        form2 = {"010": 1_000_000.0, "250": 150_000.0}
        result = compute(None, form2)
        assert result["absolutes"]["netProfit"] == 150_000.0
        assert result["ratios"]["netMargin"] == pytest.approx(0.15)
