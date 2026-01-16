"""
Utilities for validating string inputs.
"""
from datetime import datetime
import secrets
import string

from securypi_app.services.app_config import AppConfig


def validate_str_input_len(input,
                           min_len,
                           max_len,
                           expr_name="expression") -> None | str:
    """
    Check if input string length is within given limits. 
    Return None if valid, otherwise return error message.
    """
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
    """
    Check if username string length is within given limits. 
    Return None if valid, otherwise return error message.
    """
    config = AppConfig.get()
    min_username_len = config.authentication.username.min_length
    max_username_len = config.authentication.username.max_length
    return validate_str_input_len(username,
                                  min_len=min_username_len,
                                  max_len=max_username_len,
                                  expr_name="user name")


def validate_str_password(password) -> None | str:
    """
    Check if password string length is within given limits.
    Return None if valid, otherwise return error message.
    """
    config = AppConfig.get()
    min_pw_len = config.authentication.password.min_length
    max_pw_len = config.authentication.password.max_length
    return validate_str_input_len(password,
                                  min_len=min_pw_len,
                                  max_len=max_pw_len,
                                  expr_name="password")


def timed_filename(file_type="") -> str:
    """
    Return a name of the file
    consisting from current date and time.
    file_type examples: "mp4", ".mp4", txt", ".json"
    """
    if file_type:
        file_type = file_type.strip(".")
    # user might pass "."
    if file_type:
        file_type = "." + file_type
    
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + file_type

def generate_random_password_formatted() -> str:
    """
    Returns cryptographically secure
    password in format: 'Aa99Aa99Aaaa' (12 chars)
    """
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits

    password_chars = []

    # 'Aa99' * 2
    for _ in range(2):  # 'Aa9' repeated twice
        password_chars.append(secrets.choice(uppercase))
        password_chars.append(secrets.choice(lowercase))
        password_chars.append(secrets.choice(digits))
        password_chars.append(secrets.choice(digits))

    # Final 'Aaa'
    password_chars.append(secrets.choice(uppercase))
    password_chars.append(secrets.choice(lowercase))
    password_chars.append(secrets.choice(lowercase))
    password_chars.append(secrets.choice(lowercase))

    return ''.join(password_chars)

def generate_random_password(n) -> str:
    """ Returns cryptographically secure password in format: 'Aa99Aa99Aaaa' """
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    all = uppercase + lowercase + digits

    password_chars = []

    for _ in range(n):
       password_chars.append(secrets.choice(all))

    return ''.join(password_chars)
