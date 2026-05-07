"""Tests for app.auth — password hashing and JWT tokens."""

from app.auth import hash_password, verify_password, create_access_token, decode_token


class TestHashPassword:
    def test_returns_hash_different_from_input(self):
        password = "my-secret-password"
        hashed = hash_password(password)
        assert hashed != password
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_different_calls_produce_different_hashes(self):
        # bcrypt uses random salts, so two hashes of the same password differ
        h1 = hash_password("same-password")
        h2 = hash_password("same-password")
        assert h1 != h2


class TestVerifyPassword:
    def test_returns_true_for_correct_password(self):
        password = "correct-password"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_returns_false_for_wrong_password(self):
        hashed = hash_password("correct-password")
        assert verify_password("wrong-password", hashed) is False


class TestCreateAccessToken:
    def test_returns_string_token(self):
        token = create_access_token(user_id="user-123", role="student")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_has_three_parts(self):
        # JWTs have header.payload.signature
        token = create_access_token(user_id="user-123", role="admin")
        parts = token.split(".")
        assert len(parts) == 3


class TestDecodeToken:
    def test_decodes_token_created_by_create_access_token(self):
        token = create_access_token(user_id="user-456", role="teacher")
        payload = decode_token(token)
        assert payload["sub"] == "user-456"
        assert payload["role"] == "teacher"
        assert "exp" in payload

    def test_roundtrip_preserves_user_id_and_role(self):
        user_id = "abc-def-ghi"
        role = "admin"
        token = create_access_token(user_id=user_id, role=role)
        payload = decode_token(token)
        assert payload["sub"] == user_id
        assert payload["role"] == role

    def test_invalid_token_raises_http_exception(self):
        from fastapi import HTTPException
        import pytest

        with pytest.raises(HTTPException) as exc_info:
            decode_token("invalid.token.string")
        assert exc_info.value.status_code == 401
