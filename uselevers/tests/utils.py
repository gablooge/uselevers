import random
import string


def random_lower_string(n: int) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=n))
