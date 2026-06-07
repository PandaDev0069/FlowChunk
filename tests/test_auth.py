import bcrypt

from app.core.auth import hash_password, verify_password


def test_hash_password_supports_long_passwords() -> None:
    password = "x" * 100

    hashed_password = hash_password(password)

    assert hashed_password.startswith("$pbkdf2-sha256$")
    assert verify_password(password, hashed_password)


def test_verify_password_accepts_existing_bcrypt_hashes() -> None:
    legacy_hash = bcrypt.hashpw(b"legacy-password", bcrypt.gensalt()).decode("utf-8")

    assert verify_password("legacy-password", legacy_hash)
