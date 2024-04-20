import random
import string


def generate_code(length: int = 4, referral: bool = False):
    """Code generator."""
    digits = string.digits
    if referral:
        digits += string.ascii_uppercase
    return ''.join(random.choice(digits) for _ in range(length))
