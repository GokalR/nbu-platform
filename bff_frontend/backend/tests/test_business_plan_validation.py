"""Tests for app.services.business_plan_validation — input gate + output validator.

Also covers `business_plan_client._assemble_full_plan` which is the slim-schema
counterpart that runs *before* the validator: takes the LLM's qualitative-only
output and merges it with deterministic numbers + catalog data into the full
plan shape.
"""

from __future__ import annotations

import pytest

from app.services import business_plan_client as bpc_client
from app.services import business_plan_compute as bpc
from app.services import business_plan_validation as bpv
from app.services import credit_scoring, nbu_products


# ---------- fixtures: realistic bakery payload from the wizard's quick-template ----------

@pytest.fixture
def bakery_inputs() -> dict:
    return {
        "organization": {
            "type": "legal_entity",
            "inn": "126156934",
            "name": "Issiq Non Ishlab Chiqarish",
            "address": "Toshkent shahri, Yunusobod tumani",
            "foundedDate": "2024-04-07",
            "mainActivity": "Non mahsulotlarini ishlab chiqarish",
            "founder": "Muhsinov Alisher",
            "charterCapital": 50_000_000,
        },
        "project": {
            "purpose": "Oylik 85 000 dona quvvatga ega non zavodini ochish",
            "location": "Toshkent shahri, Yunusobod tumani",
            "ownContribution": 50_000_000,
            "loanAmount": 250_000_000,
            "totalValue": 300_000_000,
            "startupMonths": 3,
            "termMonths": 36,
            "graceMonths": 6,
            "interestRate": 24,
        },
        "assets": {
            "creditFinanced": [{"name": "Pech", "qty": 2, "unit": "dona"}],
            "selfFinanced": [],
        },
        "products": [
            {"name": "1-navli non", "monthlyVolume": 35_000, "price": 3_950, "currency": "UZS"},
            {"name": "2-navli non", "monthlyVolume": 50_000, "price": 3_500, "currency": "UZS"},
        ],
        "team": [
            {"role": "Nonvoy", "count": 8, "salary": 5_500_000},
            {"role": "Buxgalter", "count": 1, "salary": 6_000_000},
        ],
        "utilities": {
            "electricityKwh": 2300, "gasM3": 4000, "waterM3": 2000,
            "extras": [
                {"name": "Ijara", "amount": 8_000_000},
                {"name": "Un", "amount": 120_000_000},
            ],
        },
    }


@pytest.fixture
def bakery_baseline(bakery_inputs):
    return bpc.compute_baseline(bakery_inputs)


@pytest.fixture
def bakery_credit_score(bakery_inputs, bakery_baseline):
    return credit_scoring.compute_wizard_score(bakery_inputs, bakery_baseline)


@pytest.fixture
def bakery_candidates(bakery_inputs):
    p = bakery_inputs["project"]
    return nbu_products.select_candidates(
        loan_amount_uzs=p["loanAmount"], term_months=p["termMonths"],
        client_type=bakery_inputs["organization"]["type"],
        assets_credit=bakery_inputs["assets"]["creditFinanced"],
        project_purpose=p["purpose"], top_n=3,
    )


# ============================================================================
# Input gate
# ============================================================================

class TestValidateInputs:
    def test_valid_bakery_passes(self, bakery_inputs, bakery_baseline, bakery_candidates):
        errors, warnings = bpv.validate_inputs(bakery_inputs, bakery_baseline, bakery_candidates)
        assert errors == []

    def test_zero_revenue_blocks(self, bakery_inputs, bakery_candidates):
        bakery_inputs["products"] = []
        baseline = bpc.compute_baseline(bakery_inputs)
        errors, _ = bpv.validate_inputs(bakery_inputs, baseline, bakery_candidates)
        assert any("выручка" in e["message"].lower() or "products" in e["field"]
                   for e in errors)

    def test_loan_zero_blocks(self, bakery_inputs, bakery_baseline, bakery_candidates):
        bakery_inputs["project"]["loanAmount"] = 0
        errors, _ = bpv.validate_inputs(bakery_inputs, bakery_baseline, bakery_candidates)
        assert any(e["field"] == "project.loanAmount" for e in errors)

    def test_total_value_mismatch_blocks(self, bakery_inputs, bakery_baseline, bakery_candidates):
        bakery_inputs["project"]["totalValue"] = 999_999_999  # not own + loan
        errors, _ = bpv.validate_inputs(bakery_inputs, bakery_baseline, bakery_candidates)
        assert any(e["field"] == "project.totalValue" for e in errors)

    def test_grace_exceeds_term_blocks(self, bakery_inputs, bakery_baseline, bakery_candidates):
        bakery_inputs["project"]["graceMonths"] = 40
        bakery_inputs["project"]["termMonths"] = 36
        errors, _ = bpv.validate_inputs(bakery_inputs, bakery_baseline, bakery_candidates)
        assert any(e["field"] == "project.graceMonths" for e in errors)

    def test_interest_rate_out_of_range_blocks(self, bakery_inputs, bakery_baseline, bakery_candidates):
        bakery_inputs["project"]["interestRate"] = 200
        errors, _ = bpv.validate_inputs(bakery_inputs, bakery_baseline, bakery_candidates)
        assert any(e["field"] == "project.interestRate" for e in errors)

    def test_future_founded_date_blocks(self, bakery_inputs, bakery_baseline, bakery_candidates):
        bakery_inputs["organization"]["foundedDate"] = "2099-01-01"
        errors, _ = bpv.validate_inputs(bakery_inputs, bakery_baseline, bakery_candidates)
        assert any(e["field"] == "organization.foundedDate" for e in errors)

    def test_invalid_founded_date_format_blocks(self, bakery_inputs, bakery_baseline, bakery_candidates):
        bakery_inputs["organization"]["foundedDate"] = "not-a-date"
        errors, _ = bpv.validate_inputs(bakery_inputs, bakery_baseline, bakery_candidates)
        assert any(e["field"] == "organization.foundedDate" for e in errors)

    def test_salary_too_low_blocks(self, bakery_inputs, bakery_baseline, bakery_candidates):
        bakery_inputs["team"][0]["salary"] = 100_000  # below min
        errors, _ = bpv.validate_inputs(bakery_inputs, bakery_baseline, bakery_candidates)
        assert any(e["field"].startswith("team[") for e in errors)

    def test_salary_absurdly_high_blocks(self, bakery_inputs, bakery_baseline, bakery_candidates):
        bakery_inputs["team"][0]["salary"] = 999_000_000_000
        errors, _ = bpv.validate_inputs(bakery_inputs, bakery_baseline, bakery_candidates)
        assert any(e["field"].startswith("team[") for e in errors)

    def test_no_candidates_blocks(self, bakery_inputs, bakery_baseline):
        errors, _ = bpv.validate_inputs(bakery_inputs, bakery_baseline, [])
        assert any("каталог" in e["message"].lower() for e in errors)

    def test_loss_making_warns_only(self, bakery_inputs, bakery_candidates):
        # Inflate costs to push profit negative without other rule violations
        bakery_inputs["utilities"]["extras"].append({"name": "Massive", "amount": 5_000_000_000})
        baseline = bpc.compute_baseline(bakery_inputs)
        errors, warnings = bpv.validate_inputs(bakery_inputs, baseline, bakery_candidates)
        assert errors == []
        assert any("прибыль" in w["message"].lower() or "убыточ" in w["message"].lower()
                   for w in warnings)

    def test_fx_products_warn_only(self, bakery_inputs, bakery_candidates):
        bakery_inputs["products"][0]["currency"] = "USD"
        baseline = bpc.compute_baseline(bakery_inputs)
        errors, warnings = bpv.validate_inputs(bakery_inputs, baseline, bakery_candidates)
        # Other UZS product still keeps revenue > 0
        assert errors == []
        assert any("валют" in w["message"].lower() for w in warnings)

    def test_non_string_role_does_not_crash(
        self, bakery_inputs, bakery_baseline, bakery_candidates
    ):
        """Regression: validate_inputs must coerce non-string `role` values
        instead of crashing with 'int has no attribute strip'."""
        bakery_inputs["team"] = [
            {"role": 12345, "count": 1, "salary": 5_000_000},  # int role
        ]
        # Should not raise
        errors, warnings = bpv.validate_inputs(
            bakery_inputs, bakery_baseline, bakery_candidates,
        )
        # Salary is in band; no team-related errors expected
        assert not any(e["field"].startswith("team[") for e in errors)


# ============================================================================
# Output validator
# ============================================================================

class TestValidateAndClean:
    def _llm_skeleton(self) -> dict:
        # Minimal "valid" LLM output we can mutate per-test.
        return {
            "feasibilityVerdict": "high",
            "feasibilityScore": 95,                      # validator must overwrite
            "summary": "Краткое резюме.",
            "executiveSummary": "Резюме для банка.",
            "marketContext": "Хлебобулочный сегмент стабилен.",
            "operations": {"processFlow": ["мес"], "supplyChain": "Мука", "criticalDependencies": []},
            "team": {"totalHeadcount": 9, "monthlyPayroll": 50_000_000, "annualPayroll": 600_000_000,
                     "assessment": "OK"},
            "financials": {
                "monthlyRevenue": 313_250_000,
                "monthlyCosts": {"payroll": 50_000_000, "utilities": 20_270_000,
                                 "rawMaterials": 120_000_000, "loanPayment": 10_000_000,
                                 "rent": 8_000_000, "other": 0, "total": 208_270_000},
                "monthlyProfit": 105_000_000, "annualProfit": 1_260_000_000,
                "breakevenMonths": 5, "grossMarginPct": 35.0, "ebitdaMarginPct": 30.0,
                "assessment": "OK",
            },
            "projection12m": [
                {"month": i, "revenue": 100_000_000, "costs": 80_000_000, "profit": 20_000_000}
                for i in range(1, 13)
            ],
            "milestones": {"first90Days": ["a"], "first6Months": ["b"], "first12Months": ["c"]},
            "risks": [
                {"type": "market", "severity": "medium", "description": "конкуренция", "mitigation": "цена"},
            ],
            "kpis": [
                {"name": "Выручка", "target": "300М", "frequency": "ежемесячно"},
            ],
            "recommendedProducts": [],
            "actionableNextSteps": ["шаг 1"],
        }

    def test_feasibility_overwritten_from_credit_score(
        self, bakery_baseline, bakery_credit_score, bakery_candidates, bakery_inputs
    ):
        out = self._llm_skeleton()
        out["feasibilityScore"] = 95
        out["feasibilityVerdict"] = "high"
        cleaned = bpv.validate_and_clean(
            out, candidates=bakery_candidates, baseline=bakery_baseline,
            credit_score=bakery_credit_score, inputs=bakery_inputs,
        )
        assert cleaned["feasibilityVerdict"] == bakery_credit_score["verdict"]
        assert cleaned["feasibilityScore"] == int(bakery_credit_score["percent"])

    def test_hallucinated_product_dropped(
        self, bakery_baseline, bakery_credit_score, bakery_candidates, bakery_inputs
    ):
        out = self._llm_skeleton()
        out["recommendedProducts"] = [
            {"productId": "fake_product_xyz", "name": "Fake", "rate": "5%",
             "rationale": "...", "fitScore": 90},
        ]
        cleaned = bpv.validate_and_clean(
            out, candidates=bakery_candidates, baseline=bakery_baseline,
            credit_score=bakery_credit_score, inputs=bakery_inputs,
        )
        assert cleaned["recommendedProducts"] == []
        assert cleaned.get("_validity", {}).get("noProductMatch") is True

    def test_real_product_hydrated_from_catalog(
        self, bakery_baseline, bakery_credit_score, bakery_candidates, bakery_inputs
    ):
        out = self._llm_skeleton()
        real_id = bakery_candidates[0]["id"]
        out["recommendedProducts"] = [
            {"productId": real_id, "name": "WRONG NAME", "rate": "999%",
             "rationale": "fits well", "fitScore": 80},
        ]
        cleaned = bpv.validate_and_clean(
            out, candidates=bakery_candidates, baseline=bakery_baseline,
            credit_score=bakery_credit_score, inputs=bakery_inputs,
        )
        assert len(cleaned["recommendedProducts"]) == 1
        rp = cleaned["recommendedProducts"][0]
        # Hydrated from catalog, not from the LLM's wrong values
        assert rp["name"] == bakery_candidates[0]["name"]
        assert rp["rate"] == bakery_candidates[0]["rate"]
        assert rp["rationale"] == "fits well"

    def test_broken_projection_replaced_with_synth(
        self, bakery_baseline, bakery_credit_score, bakery_candidates, bakery_inputs
    ):
        out = self._llm_skeleton()
        out["projection12m"] = [{"month": 1, "revenue": "abc"}]  # broken
        cleaned = bpv.validate_and_clean(
            out, candidates=bakery_candidates, baseline=bakery_baseline,
            credit_score=bakery_credit_score, inputs=bakery_inputs,
        )
        assert len(cleaned["projection12m"]) == 12
        assert cleaned["_validity"]["projectionSource"] == "synthesized"
        assert all(isinstance(p["revenue"], int) for p in cleaned["projection12m"])

    def test_invalid_risk_dropped(
        self, bakery_baseline, bakery_credit_score, bakery_candidates, bakery_inputs
    ):
        out = self._llm_skeleton()
        out["risks"] = [
            {"type": "competitive", "severity": "очень высокая",  # bad enums
             "description": "x", "mitigation": "y"},
            {"type": "market", "severity": "high",
             "description": "valid risk", "mitigation": "valid mit"},
        ]
        cleaned = bpv.validate_and_clean(
            out, candidates=bakery_candidates, baseline=bakery_baseline,
            credit_score=bakery_credit_score, inputs=bakery_inputs,
        )
        # Only the valid one survives (plus any warning-derived risks the
        # validator may have appended — none for this fixture).
        valid_risks = [r for r in cleaned["risks"] if r["type"] == "market"]
        assert len(valid_risks) == 1

    def test_market_context_with_quant_claim_blanked(
        self, bakery_baseline, bakery_credit_score, bakery_candidates, bakery_inputs
    ):
        out = self._llm_skeleton()
        out["marketContext"] = "Рынок составил 4.2 трлн сум в 2024 году."
        cleaned = bpv.validate_and_clean(
            out, candidates=bakery_candidates, baseline=bakery_baseline,
            credit_score=bakery_credit_score, inputs=bakery_inputs,
        )
        assert cleaned["marketContext"] == ""
        assert cleaned["_validity"]["marketContextBlanked"] is True

    def test_market_context_without_numbers_kept(
        self, bakery_baseline, bakery_credit_score, bakery_candidates, bakery_inputs
    ):
        out = self._llm_skeleton()
        out["marketContext"] = "Хлебобулочный сегмент стабилен и растёт."
        cleaned = bpv.validate_and_clean(
            out, candidates=bakery_candidates, baseline=bakery_baseline,
            credit_score=bakery_credit_score, inputs=bakery_inputs,
        )
        assert cleaned["marketContext"] == "Хлебобулочный сегмент стабилен и растёт."

    def test_unparseable_llm_output_returns_skeleton(
        self, bakery_baseline, bakery_credit_score, bakery_candidates, bakery_inputs
    ):
        cleaned = bpv.validate_and_clean(
            "garbage string, not a dict",  # type: ignore[arg-type]
            candidates=bakery_candidates, baseline=bakery_baseline,
            credit_score=bakery_credit_score, inputs=bakery_inputs,
        )
        assert isinstance(cleaned, dict)
        assert cleaned["_validity"]["llmOutputUnusable"] is True
        assert len(cleaned["projection12m"]) == 12

    def test_extras_categorization_mismatch_falls_back_to_lump(
        self, bakery_baseline, bakery_credit_score, bakery_candidates, bakery_inputs
    ):
        out = self._llm_skeleton()
        # extras.total is 128M; misallocate so categorization sums to 50M
        out["financials"]["monthlyCosts"]["rent"] = 10_000_000
        out["financials"]["monthlyCosts"]["rawMaterials"] = 30_000_000
        out["financials"]["monthlyCosts"]["other"] = 10_000_000
        cleaned = bpv.validate_and_clean(
            out, candidates=bakery_candidates, baseline=bakery_baseline,
            credit_score=bakery_credit_score, inputs=bakery_inputs,
        )
        mc = cleaned["financials"]["monthlyCosts"]
        assert mc["rent"] == 0
        assert mc["rawMaterials"] == 0
        assert mc["other"] == int(bakery_baseline["extras"]["total"])
        assert cleaned["_validity"]["extrasFallback"] is True

    def test_breakeven_derived_from_projection(
        self, bakery_baseline, bakery_credit_score, bakery_candidates, bakery_inputs
    ):
        out = self._llm_skeleton()
        # Build a projection that breaks even at month 4
        out["projection12m"] = [
            {"month": 1, "revenue": 50, "costs": 100, "profit": -50},
            {"month": 2, "revenue": 50, "costs": 100, "profit": -50},
            {"month": 3, "revenue": 50, "costs": 100, "profit": -50},
            {"month": 4, "revenue": 200, "costs": 50, "profit": 150},  # cum=0
        ] + [
            {"month": i, "revenue": 200, "costs": 50, "profit": 150}
            for i in range(5, 13)
        ]
        cleaned = bpv.validate_and_clean(
            out, candidates=bakery_candidates, baseline=bakery_baseline,
            credit_score=bakery_credit_score, inputs=bakery_inputs,
        )
        assert cleaned["financials"]["breakevenMonths"] == 4

    def test_no_breakeven_returns_none(
        self, bakery_baseline, bakery_credit_score, bakery_candidates, bakery_inputs
    ):
        out = self._llm_skeleton()
        out["projection12m"] = [
            {"month": i, "revenue": 50, "costs": 100, "profit": -50}
            for i in range(1, 13)
        ]
        cleaned = bpv.validate_and_clean(
            out, candidates=bakery_candidates, baseline=bakery_baseline,
            credit_score=bakery_credit_score, inputs=bakery_inputs,
        )
        assert cleaned["financials"]["breakevenMonths"] is None

    def test_llm_returning_int_for_string_field_does_not_crash(
        self, bakery_baseline, bakery_credit_score, bakery_candidates, bakery_inputs
    ):
        """Defends against 'int' object has no attribute 'strip'.

        The LLM sometimes returns raw numbers where the schema expects
        strings (e.g. kpi.target: 85000 instead of "85 000 шт/мес").
        validate_and_clean must coerce, not crash.
        """
        out = self._llm_skeleton()
        # All four common offender fields fed non-string values:
        out["risks"] = [
            {"type": "market", "severity": "medium",
             "description": 12345,       # ← int!
             "mitigation": True},         # ← bool!
        ]
        out["kpis"] = [
            {"name": 99,                  # ← int
             "target": 85000,             # ← int (most common LLM mistake)
             "frequency": 1},             # ← int
        ]
        out["marketContext"] = 42         # ← int
        # Should NOT raise; should just filter/clean what's left
        cleaned = bpv.validate_and_clean(
            out, candidates=bakery_candidates, baseline=bakery_baseline,
            credit_score=bakery_credit_score, inputs=bakery_inputs,
        )
        # Risk survived (description/mitigation now non-empty after coerce)
        market_risks = [r for r in cleaned["risks"] if r["type"] == "market"]
        assert len(market_risks) >= 1
        assert market_risks[0]["description"] == "12345"
        # KPI survived (name "99" + target "85000" non-empty)
        assert len(cleaned["kpis"]) >= 1
        assert cleaned["kpis"][0]["target"] == "85000"
        # marketContext doesn't contain quantitative markers as a bare int,
        # so it gets through to the length cap (not blanked).
        assert isinstance(cleaned.get("marketContext"), str)


# ============================================================================
# Projection synthesis
# ============================================================================

class TestSynthesizeProjection12m:
    def test_returns_exactly_12_months(self, bakery_baseline, bakery_inputs):
        proj = bpv.synthesize_projection_12m(bakery_baseline, bakery_inputs["project"])
        assert len(proj) == 12
        assert [p["month"] for p in proj] == list(range(1, 13))

    def test_revenue_ramps_up(self, bakery_baseline, bakery_inputs):
        proj = bpv.synthesize_projection_12m(bakery_baseline, bakery_inputs["project"])
        target = bakery_baseline["revenue"]["monthlyRevenueUzs"]
        # First month is below target, last month is at target
        assert proj[0]["revenue"] < target
        assert proj[-1]["revenue"] == target

    def test_profit_consistent_with_revenue_minus_costs(
        self, bakery_baseline, bakery_inputs
    ):
        proj = bpv.synthesize_projection_12m(bakery_baseline, bakery_inputs["project"])
        for p in proj:
            assert p["profit"] == p["revenue"] - p["costs"]


# ============================================================================
# Slim-schema assembler (business_plan_client._assemble_full_plan)
# ============================================================================

class TestAssembleFullPlan:
    """Verify the assembler turns slim LLM output + deterministic data into a
    full plan with the right shape and the right sources for each field."""

    def _slim_llm_output(self, product_id: str) -> dict:
        return {
            "summary": "Краткое резюме",
            "executiveSummary": "Резюме для банка",
            "marketContext": "Качественное описание ниши",
            "operations": {
                "processFlow": ["Замес", "Выпечка", "Доставка"],
                "supplyChain": "Мука от двух поставщиков",
                "criticalDependencies": ["Электричество", "Поставщик муки"],
            },
            "teamAssessment": "Штат адекватен объёмам",
            "financialsAssessment": "Маржа умеренная, есть запас",
            "extrasCategorization": {"rent": 8_000_000, "rawMaterials": 120_000_000, "other": 0},
            "milestones": {
                "first90Days": ["Установка печей"],
                "first6Months": ["Выход на проектную мощность"],
                "first12Months": ["Расширение каналов"],
            },
            "risks": [
                {"type": "market", "severity": "medium",
                 "description": "Конкуренция с локальными пекарнями",
                 "mitigation": "Дифференциация по качеству"},
            ],
            "kpis": [
                {"name": "Выручка", "target": "313М/мес", "frequency": "ежемесячно"},
            ],
            "recommendedProducts": [
                {"productId": product_id, "rationale": "Подходит по сумме и сроку",
                 "fitScore": 85},
            ],
            "actionableNextSteps": ["Подготовить документы"],
        }

    def test_numbers_come_from_baseline_not_llm(
        self, bakery_baseline, bakery_credit_score, bakery_candidates, bakery_inputs
    ):
        """LLM output has no numeric fields; assembler must source them from baseline."""
        slim = self._slim_llm_output(bakery_candidates[0]["id"])
        plan = bpc_client._assemble_full_plan(
            slim=slim, baseline=bakery_baseline, credit_score=bakery_credit_score,
            candidates=bakery_candidates, project=bakery_inputs["project"],
        )
        # Team numbers from baseline
        assert plan["team"]["totalHeadcount"] == bakery_baseline["team"]["totalHeadcount"]
        assert plan["team"]["monthlyPayroll"] == bakery_baseline["team"]["monthlyPayroll"]
        # Revenue from baseline
        assert plan["financials"]["monthlyRevenue"] == bakery_baseline["revenue"]["monthlyRevenueUzs"]
        # Loan payment from baseline
        assert plan["financials"]["monthlyCosts"]["loanPayment"] == \
               bakery_baseline["monthlyCosts"]["breakdown"]["loanPaymentAvg"]
        # Margins from baseline
        assert plan["financials"]["grossMarginPct"] == \
               bakery_baseline["marginsAvg12m"]["grossMarginPct"]

    def test_feasibility_from_credit_score_not_llm(
        self, bakery_baseline, bakery_credit_score, bakery_candidates, bakery_inputs
    ):
        slim = self._slim_llm_output(bakery_candidates[0]["id"])
        plan = bpc_client._assemble_full_plan(
            slim=slim, baseline=bakery_baseline, credit_score=bakery_credit_score,
            candidates=bakery_candidates, project=bakery_inputs["project"],
        )
        assert plan["feasibilityVerdict"] == bakery_credit_score["verdict"]
        assert plan["feasibilityScore"] == int(bakery_credit_score["percent"])

    def test_recommended_products_hydrated_from_catalog(
        self, bakery_baseline, bakery_credit_score, bakery_candidates, bakery_inputs
    ):
        slim = self._slim_llm_output(bakery_candidates[0]["id"])
        plan = bpc_client._assemble_full_plan(
            slim=slim, baseline=bakery_baseline, credit_score=bakery_credit_score,
            candidates=bakery_candidates, project=bakery_inputs["project"],
        )
        assert len(plan["recommendedProducts"]) == 1
        rp = plan["recommendedProducts"][0]
        # Hydrated fields come from catalog
        assert rp["name"] == bakery_candidates[0]["name"]
        assert rp["rate"] == bakery_candidates[0]["rate"]
        assert rp["term"] == bakery_candidates[0]["term"]
        # Qualitative fields from LLM
        assert rp["rationale"] == "Подходит по сумме и сроку"
        assert rp["fitScore"] == 85

    def test_hallucinated_product_id_dropped(
        self, bakery_baseline, bakery_credit_score, bakery_candidates, bakery_inputs
    ):
        slim = self._slim_llm_output("totally_fake_id")
        plan = bpc_client._assemble_full_plan(
            slim=slim, baseline=bakery_baseline, credit_score=bakery_credit_score,
            candidates=bakery_candidates, project=bakery_inputs["project"],
        )
        assert plan["recommendedProducts"] == []

    def test_projection_synthesized(
        self, bakery_baseline, bakery_credit_score, bakery_candidates, bakery_inputs
    ):
        slim = self._slim_llm_output(bakery_candidates[0]["id"])
        plan = bpc_client._assemble_full_plan(
            slim=slim, baseline=bakery_baseline, credit_score=bakery_credit_score,
            candidates=bakery_candidates, project=bakery_inputs["project"],
        )
        assert len(plan["projection12m"]) == 12
        # Last month should hit target revenue
        assert plan["projection12m"][-1]["revenue"] == \
               bakery_baseline["revenue"]["monthlyRevenueUzs"]

    def test_extras_categorization_scaled_to_baseline_total(
        self, bakery_baseline, bakery_credit_score, bakery_candidates, bakery_inputs
    ):
        # LLM split sums to less than the baseline.extras.total — should
        # get scaled up so the user sees a categorization that matches reality.
        slim = self._slim_llm_output(bakery_candidates[0]["id"])
        slim["extrasCategorization"] = {"rent": 1_000_000, "rawMaterials": 10_000_000, "other": 0}
        plan = bpc_client._assemble_full_plan(
            slim=slim, baseline=bakery_baseline, credit_score=bakery_credit_score,
            candidates=bakery_candidates, project=bakery_inputs["project"],
        )
        mc = plan["financials"]["monthlyCosts"]
        scaled_total = mc["rent"] + mc["rawMaterials"] + mc["other"]
        assert scaled_total == bakery_baseline["extras"]["total"]

    def test_garbage_llm_output_still_produces_valid_plan(
        self, bakery_baseline, bakery_credit_score, bakery_candidates, bakery_inputs
    ):
        """If the LLM returns nothing useful, the assembler still emits the
        deterministic skeleton — numbers, projection, verdict — with empty
        narrative. Validator can hedge the rest from there."""
        plan = bpc_client._assemble_full_plan(
            slim={}, baseline=bakery_baseline, credit_score=bakery_credit_score,
            candidates=bakery_candidates, project=bakery_inputs["project"],
        )
        assert plan["feasibilityVerdict"] == bakery_credit_score["verdict"]
        assert plan["financials"]["monthlyRevenue"] == bakery_baseline["revenue"]["monthlyRevenueUzs"]
        assert len(plan["projection12m"]) == 12
        assert plan["recommendedProducts"] == []
        assert plan["risks"] == []

    def test_assembled_plan_passes_validator_unchanged(
        self, bakery_baseline, bakery_credit_score, bakery_candidates, bakery_inputs
    ):
        """The assembler and validator should compose: a clean assembled plan
        should pass through the validator without major rewrites."""
        slim = self._slim_llm_output(bakery_candidates[0]["id"])
        plan = bpc_client._assemble_full_plan(
            slim=slim, baseline=bakery_baseline, credit_score=bakery_credit_score,
            candidates=bakery_candidates, project=bakery_inputs["project"],
        )
        cleaned = bpv.validate_and_clean(
            plan, candidates=bakery_candidates, baseline=bakery_baseline,
            credit_score=bakery_credit_score, inputs=bakery_inputs,
        )
        # Numbers preserved
        assert cleaned["financials"]["monthlyRevenue"] == \
               bakery_baseline["revenue"]["monthlyRevenueUzs"]
        # Recommended product preserved
        assert len(cleaned["recommendedProducts"]) == 1
        # Validator should have set breakeven from the synthesized projection
        assert "breakevenMonths" in cleaned["financials"]
