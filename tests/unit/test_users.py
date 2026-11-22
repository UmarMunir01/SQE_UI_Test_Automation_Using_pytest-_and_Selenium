import pytest

from app.services.user_service import UserService


@pytest.mark.parametrize(
    "email,username,password,confirmation,expected_error",
    [
        ("person@example.com", "ab", "abc123", "abc123", None),
        ("person@example.com", "u" * 150, "Strong123", "Strong123", None),
        ("person@example.com", "user", "abc123", None, None),
        ("qa+tag@example.co.uk", "user_2", "letter1", "letter1", None),
        ("bad", "valid", "Strong123", "Strong123", "Invalid email address format"),
        ("person@example.com", "a", "Strong123", "Strong123", "Username must be greater than 1 character"),
        ("person@example.com", "u" * 151, "Strong123", "Strong123", "Username is too long (max 150 characters)"),
        ("person@example.com", "valid", "abc12", "abc12", "Password must be at least 6 characters long"),
        ("person@example.com", "valid", "123456", "123456", "Password must contain letters"),
        ("person@example.com", "valid", "Strong123", "Strong124", "Passwords do not match"),
    ],
)
def test_validate_user_data_equivalence_and_boundary_classes(
    email, username, password, confirmation, expected_error
):
    errors = UserService.validate_user_data(email, username, password, confirmation)

    if expected_error is None:
        assert errors == []
    else:
        assert expected_error in errors


@pytest.mark.parametrize(
    "scenario,username,email,password,confirmation,expected_success",
    [
        ("minimum_username", "ab", "minimum@example.com", "abc123", "abc123", True),
        ("maximum_username", "u" * 150, "maximum@example.com", "Strong123", "Strong123", True),
        ("normal_values", "normal-user", "normal@example.com", "letter1", "letter1", True),
        ("unicode_username", "unicode-ü", "unicode@example.com", "Strong123", "Strong123", True),
        ("invalid_email", "valid-user", "bad-email", "Strong123", "Strong123", False),
        ("short_username", "a", "short@example.com", "Strong123", "Strong123", False),
        ("weak_password", "valid-user", "weak@example.com", "123456", "123456", False),
        ("password_mismatch", "valid-user", "mismatch@example.com", "Strong123", "Strong124", False),
        ("duplicate_email", "new-user", "existing@example.com", "Strong123", None, False),
        ("duplicate_username", "existing-user", "new@example.com", "Strong123", None, False),
    ],
)
def test_create_user_equivalence_and_duplicate_partitions(
    app, scenario, username, email, password, confirmation, expected_success
):
    with app.app_context():
        if scenario.startswith("duplicate_"):
            UserService.create_user("existing@example.com", "existing-user", "Strong123")

        result = UserService.create_user(email, username, password, confirmation)

        assert result["success"] is expected_success
        if expected_success:
            assert result["user"].user_name == username
        else:
            assert result["errors"]


@pytest.mark.parametrize(
    "username,password,expected_success",
    [
        ("known-user", "Strong123", True),
        ("missing-user", "Strong123", False),
        ("known-user", "Wrong123", False),
        ("", "Strong123", False),
        ("known-user", "", False),
        ("KNOWN-USER", "Strong123", False),
        (" ", "Strong123", False),
        ("known-user", "strong123", False),
    ],
)
def test_authenticate_user_equivalence_classes(app, user_factory, username, password, expected_success):
    with app.app_context():
        user_factory(username="known-user", email="known@example.com")

        result = UserService.authenticate_user(username, password)

        assert result["success"] is expected_success


@pytest.mark.parametrize(
    "email,username,expected_exists",
    [
        ("known@example.com", "missing", True),
        ("missing@example.com", "known-user", True),
        ("known@example.com", "known-user", True),
        ("missing@example.com", "missing", False),
        ("", "", False),
        ("KNOWN@example.com", "KNOWN-USER", False),
    ],
)
def test_user_exists_matches_email_or_username(app, user_factory, email, username, expected_exists):
    with app.app_context():
        user_factory(username="known-user", email="known@example.com")

        assert UserService.user_exists(email, username) is expected_exists


@pytest.mark.parametrize(
    "id_offset,expected_exists",
    [(0, True), (-1, False), (-2, False), (1, False), (10, False), (1000, False)],
)
def test_get_user_by_id_handles_existing_and_out_of_range_ids(
    app, user_factory, id_offset, expected_exists
):
    with app.app_context():
        user = user_factory()

        result = UserService.get_user_by_id(user.id + id_offset)

        assert (result is not None) is expected_exists
