"""Tests for app.schemas — Pydantic model validation."""

from app.schemas import SubmissionCreate, AnalysisRequest, SubmissionOut, UploadOut


class TestSubmissionCreate:
    def test_accepts_valid_data(self):
        data = {
            "profile": {"name": "Test Bank", "inn": "123456789"},
            "finance": {"revenue": 1_000_000},
            "city_id": "tashkent",
            "lang": "uz",
        }
        schema = SubmissionCreate(**data)
        assert schema.profile["name"] == "Test Bank"
        assert schema.finance["revenue"] == 1_000_000
        assert schema.city_id == "tashkent"
        assert schema.lang == "uz"

    def test_defaults(self):
        schema = SubmissionCreate()
        assert schema.profile == {}
        assert schema.finance == {}
        assert schema.city_id is None
        assert schema.lang == "ru"

    def test_accepts_minimal_data(self):
        schema = SubmissionCreate(profile={"name": "X"})
        assert schema.profile == {"name": "X"}
        assert schema.finance == {}

    def test_accepts_nested_finance_data(self):
        finance = {
            "form1": {"010": 1000, "020": 2000},
            "form2": {"010": 5000},
        }
        schema = SubmissionCreate(finance=finance)
        assert schema.finance["form1"]["010"] == 1000


class TestAnalysisRequest:
    def test_all_fields_optional(self):
        schema = AnalysisRequest()
        assert schema.lang is None
        assert schema.model is None

    def test_with_lang(self):
        schema = AnalysisRequest(lang="uz")
        assert schema.lang == "uz"

    def test_with_model(self):
        schema = AnalysisRequest(model="claude-sonnet-4-6")
        assert schema.model == "claude-sonnet-4-6"

    def test_with_all_fields(self):
        schema = AnalysisRequest(lang="ru", model="claude-sonnet-4-6")
        assert schema.lang == "ru"
        assert schema.model == "claude-sonnet-4-6"
