import pytest

from app.utils.helpers import sanitize_input, validate_email, validate_password_strength


@pytest.mark.parametrize(
    "email",
    [
        "person@example.com",
        "first.last@sub.domain.co.uk",
        "x+y@example.org",
        "USER_01@EXAMPLE.NET",
        "qa-team@sample.io",
    ],
)
def test_validate_email_accepts_valid_equivalence_classes(email):
    assert validate_email(email) is True


@pytest.mark.parametrize(
    "email",
    [None, "", "plain-text", "person@", "two@@example.com"],
)
def test_validate_email_rejects_invalid_equivalence_classes(email):
    assert validate_email(email) is False


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, ""),
        ("", ""),
        ("   ", ""),
        (" task ", "task"),
        ("<b>Task</b>", "&lt;b&gt;Task&lt;/b&gt;"),
        ("<script>alert(1)</script>safe", "safe"),
        ("<STYLE>hidden</STYLE>safe", "safe"),
        ('say "hi"', "say &quot;hi&quot;"),
        ("a&b", "a&amp;b"),
        (123, "123"),
    ],
)
def test_sanitize_input_equivalence_classes(value, expected):
    assert sanitize_input(value) == expected


@pytest.mark.parametrize(
    "password",
    ["abc123", "Ab1234", "a" * 5 + "1", "A1" + "b" * 4, "z" * 20 + "9"],
)
def test_password_strength_accepts_valid_length_and_character_classes(password):
    assert validate_password_strength(password) == []


@pytest.mark.parametrize(
    "password,expected_error",
    [
        (None, "Password is required"),
        ("abc12", "Password must be at least 6 characters long"),
        ("12345", "Password must be at least 6 characters long"),
        ("123456", "Password must contain letters"),
        ("abcdef", "Password must contain numbers"),
    ],
)
def test_password_strength_rejects_invalid_or_below_boundary_values(password, expected_error):
    assert expected_error in validate_password_strength(password)
