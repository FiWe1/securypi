"""
Utilities for validating string inputs.
"""

MIN_USERNAME_LENGTH = 4
MIN_PASSWORD_LENGTH = 8
MAX_USERNAME_LENGTH = 16
MAX_PASSWORD_LENGTH = 64


def validate_str_input_len(input,
                           min_len,
                           max_len,
                           expr_name="expression") -> None | str:
    error = None
    if not input:
        error = f"{expr_name} is required!"
    elif len(input) < min_len:
        error = (
            f"{expr_name} is too short; must be between: {min_len} - {max_len}"
        )
    elif len(input) > max_len:
        error = (
            f"{expr_name} is too long; must be between: {min_len} - {max_len}"
        )

    return error


def validate_str_username(username) -> None | str:
    return validate_str_input_len(username,
                                  min_len=MIN_USERNAME_LENGTH,
                                  max_len=MAX_USERNAME_LENGTH,
                                  expr_name="user name")


def validate_str_password(password) -> None | str:
    return validate_str_input_len(password,
                                  min_len=MIN_PASSWORD_LENGTH,
                                  max_len=MAX_PASSWORD_LENGTH,
                                  expr_name="password")