import string
import random


def generate_name():
    chars = string.ascii_letters + string.digits  # uppercase, lowercase, and numbers
    name = ''.join((random.choice(chars) for i in range(8)))  # generate name
    return name
