from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from pathlib import Path
import settings
import string
import secrets
import sys
import os


# Check if the script was run as root
if os.geteuid() != 0:
    exit("Root privileges are necessary to run this script.\nPlease try again as root or using `sudo`.")


# Check if encryption key already exists
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
    with open(settings.ENCKEY_PATH, "rb") as kf:
        kdata = kf.read()
    return kdata


# Encrypting and storing of key
def encrypt_key(message):
    key = load_key()
    keyf = Fernet(key)

    with open('uploadkeys', 'a+') as uploadkeys:
        print(str(token), file=uploadkeys)

    with open("uploadkeys", "rb") as keyfile:
        keyfile_data = keyfile.read()

    encrypted_data = keyf.encrypt(keyfile_data)

    with open("uploadkeys", "wb") as keyfile:
        keyfile.write(encrypted_data)


def ask_yn(msg):
    resps = {"y": True, "n": False}
    ask = True
    while ask:
        proceedraw = input(msg)
        if proceedraw.lower() in resps.keys():
            proceed = resps[proceedraw]
            ask = False
        else:
            print("Invalid response.")
    return proceed


N = 64  # Size of token

# Generate key
token = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(N))

# Decrypt the existing keyfile
key = load_key()
keyf = Fernet(key)

genkey = True
uploadkeysp = Path("uploadkeys")
if not uploadkeysp.is_file():
    uploadkeysp.touch()
else:
    with open("uploadkeys", "rb") as ukf:
        # read the encrypted data
        encrypted_data = ukf.read()

    try:
        decrypted_data = keyf.decrypt(encrypted_data)  # decrypt data
        with open("uploadkeys", "wb") as ukf:
            ukf.write(decrypted_data)  # write the original file
    except InvalidToken:
        print("The encrypted key data is invalid and cannot be read.")
        print("It may be necessary to clear the file entirely, which will invalidate all tokens.")
        proceed = ask_yn("Do you wish to proceed to clearing the uploadkeys file? [y/n] ")

        if proceed:
            os.remove("uploadkeys")
            print("Removed uploadkeys file.")
            proceed2 = ask_yn("Would you like to continue and generate a new token? [y/n] ")
            if not proceed2:
                genkey = False

if genkey:
    print("Your new token is: " + str(token))  # Print token
    encrypt_key(str(token))  # Encrypt the key and save
