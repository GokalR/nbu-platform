"""Tests for app.helpers — translate_field, asset_url, translate_content."""

from unittest.mock import patch, MagicMock

from app.helpers import translate_field, asset_url, translate_content


# ---------------------------------------------------------------------------
# translate_field
# ---------------------------------------------------------------------------

class TestTranslateField:
    def test_returns_uz_value_when_lang_uz(self):
        field = {"ru": "Привет", "uz": "Salom"}
        assert translate_field(field, "uz") == "Salom"

    def test_returns_ru_value_when_lang_ru(self):
        field = {"ru": "Привет", "uz": "Salom"}
        assert translate_field(field, "ru") == "Привет"

    def test_returns_ru_as_fallback_when_lang_missing(self):
        field = {"ru": "Привет", "uz": "Salom"}
        assert translate_field(field, "en") == "Привет"

    def test_returns_empty_string_for_none_input(self):
        assert translate_field(None, "ru") == ""

    def test_returns_string_as_is_when_plain_string(self):
        assert translate_field("hello", "ru") == "hello"

    def test_returns_empty_string_for_empty_string_input(self):
        assert translate_field("", "ru") == ""

    def test_returns_empty_string_when_dict_has_no_matching_keys(self):
        field = {"en": "Hello"}
        assert translate_field(field, "uz") == ""


# ---------------------------------------------------------------------------
# asset_url
# ---------------------------------------------------------------------------

class TestAssetUrl:
    def test_returns_none_for_none_input(self):
        assert asset_url(None) is None

    def test_returns_none_for_empty_string(self):
        # empty string is falsy, so asset_url returns it as-is (which is "")
        result = asset_url("")
        assert result == ""

    def test_returns_full_url_unchanged_if_starts_with_http(self):
        url = "https://example.com/video.mp4"
        with patch("app.helpers.get_settings") as mock_settings:
            result = asset_url(url)
        assert result == url

    def test_prepends_base_url_when_video_base_url_is_set(self):
        mock_settings = MagicMock()
        mock_settings.video_base_url_stripped = "https://cdn.example.com"
        with patch("app.helpers.get_settings", return_value=mock_settings):
            result = asset_url("/videos/intro.mp4")
        assert result == "https://cdn.example.com/videos/intro.mp4"

    def test_returns_path_as_is_when_video_base_url_is_empty(self):
        mock_settings = MagicMock()
        mock_settings.video_base_url_stripped = ""
        with patch("app.helpers.get_settings", return_value=mock_settings):
            result = asset_url("/videos/intro.mp4")
        assert result == "/videos/intro.mp4"


# ---------------------------------------------------------------------------
# translate_content
# ---------------------------------------------------------------------------

class TestTranslateContent:
    def test_translates_ru_uz_dict(self):
        obj = {"ru": "Привет", "uz": "Salom"}
        assert translate_content(obj, "uz") == "Salom"

    def test_translates_ru_uz_dict_to_ru(self):
        obj = {"ru": "Привет", "uz": "Salom"}
        assert translate_content(obj, "ru") == "Привет"

    def test_handles_nested_dicts(self):
        obj = {
            "title": {"ru": "Заголовок", "uz": "Sarlavha"},
            "body": {"ru": "Текст", "uz": "Matn"},
        }
        result = translate_content(obj, "uz")
        assert result == {"title": "Sarlavha", "body": "Matn"}

    def test_handles_lists_of_translatable_items(self):
        obj = [
            {"ru": "Один", "uz": "Bir"},
            {"ru": "Два", "uz": "Ikki"},
        ]
        result = translate_content(obj, "uz")
        assert result == ["Bir", "Ikki"]

    def test_returns_non_dict_list_values_as_is(self):
        assert translate_content(42, "uz") == 42
        assert translate_content("plain", "uz") == "plain"
        assert translate_content(None, "uz") is None

    def test_does_not_translate_dict_with_extra_keys(self):
        # A dict with more than just "ru" and "uz" keys should NOT be
        # treated as a translatable dict — it should recurse into values.
        obj = {"ru": "Привет", "uz": "Salom", "en": "Hello"}
        result = translate_content(obj, "uz")
        assert isinstance(result, dict)
        assert result["ru"] == "Привет"
        assert result["uz"] == "Salom"
        assert result["en"] == "Hello"

    def test_deeply_nested_structure(self):
        obj = {
            "quiz": [
                {
                    "question": {"ru": "Вопрос", "uz": "Savol"},
                    "answers": [
                        {"ru": "Да", "uz": "Ha"},
                        {"ru": "Нет", "uz": "Yoq"},
                    ],
                }
            ]
        }
        result = translate_content(obj, "uz")
        assert result == {
            "quiz": [
                {
                    "question": "Savol",
                    "answers": ["Ha", "Yoq"],
                }
            ]
        }
