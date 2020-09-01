from cryptography.fernet import Fernet
from pathlib import Path
import settings
import string
import secrets
import sys
import os

# Check if the script is ran as root 
if os.geteuid() != 0:
    exit("Root privileges are necessary to run this script.\nPlease try again as root or using `sudo`.")

# Check if encryption key exists
enckey = Path(settings.ENCKEY_PATH)
if enckey.is_file():
	print("Encryption key found.")
else:
    print("Encryption key not found.")
    print("Generating key...")
    key = Fernet.generate_key()
    with open(settings.ENCKEY_PATH, "wb") as key_file:
        key_file.write(key)
    print("Encryption key generated and stored in secret.key.")

# Load encryption key
def load_key():
    return open(settings.ENCKEY_PATH, "rb").read()

# Set size of string
N = 64

# Generating of key
token = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(64))

# Decrypt the existing keyfile
key = load_key()
f = Fernet(key)
with open("uploadkeys", "rb") as file:
    # read the encrypted data
    encrypted_data = file.read()
# decrypt data
decrypted_data = f.decrypt(encrypted_data)
# write the original file
with open("uploadkeys", "wb") as file:
    file.write(decrypted_data)

# Encrypting and storing of key
def encrypt_key(message):
    key = load_key()
    f = Fernet(key)

    with open('uploadkeys', 'a+') as uploadkeys:
        print(str(token), file=uploadkeys)

    with open("uploadkeys", "rb") as keyfile:
        keyfile_data = keyfile.read()

    encrypted_data = f.encrypt(keyfile_data)

    with open("uploadkeys", "wb") as keyfile:
        keyfile.write(encrypted_data)

# Print result on display and call encrypt_key
print("Your new token is: " + str(token))
encrypt_key(str(token))