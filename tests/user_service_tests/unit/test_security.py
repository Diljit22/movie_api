from user_service.src.user_api import security


def test_password_hashing_and_verification():
    """
    Tests that a password can be hashed and then successfully verified.
    """
    password = "a-strong-password-123!"
    hashed_password = security.hash_password(password)

    # The hash should not be the same as the original password
    assert password != hashed_password
    # The hash should be a string
    assert isinstance(hashed_password, str)

    # Verification should succeed with the correct password
    assert security.verify_password(password, hashed_password) is True

    # Verification should fail with an incorrect password
    assert security.verify_password("wrong-password", hashed_password) is False
