from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from pathlib import Path
import settings
import string
import secrets
import sys
import os


# Load secret
def load_secret():
    with open(settings.ENCKEY_PATH, "rb") as sf:
        secret = sf.read()
    return secret


# Encrypting and storing of key
def append_uploadkey(akey):
    with open('uploadkeys', 'a+') as uploadkeysf:
        print(str(akey), file=uploadkeysf)


def decrypt_uploadkeys():
    with open("uploadkeys", "rb") as uploadkeysf:
        uploadkeys_data = uploadkeysf.read()

    try:
        secret = load_secret()
        secretf = Fernet(secret)
        decrypted_data = secretf.decrypt(uploadkeys_data)  # decrypt data
        with open("uploadkeys", "wb") as ukf:
            ukf.write(decrypted_data)  # write the original file
        print("Done decrypting")  # debug
        return True
    except InvalidToken:
        print("InvalidToken")  # debug
        print("The encrypted key data is invalid and cannot be read.")
        print("It may be necessary to clear the file entirely, which will invalidate all tokens.")
        proceed = ask_yn("Do you wish to proceed to clearing the uploadkeys file? [y/n] ")

        if proceed:
            print("Proceed1")
            os.remove("uploadkeys")
            print("Removed uploadkeys file.")
            proceed2 = ask_yn("Would you like to continue and generate a new key? [y/n] ")
            if not proceed2:
                print("not proceed2")
                return False
            else:
                print("proceed2")
                return True
        else:
            print("not Proceed1")
            return False


def encrypt_uploadkeys():
    with open("uploadkeys", "rb") as uploadkeysf:
        uploadkeys_data = uploadkeysf.read()

    secret = load_secret()
    secretf = Fernet(secret)
    encrypted_data = secretf.encrypt(uploadkeys_data)

    with open("uploadkeys", "wb") as uploadkeysf:
        uploadkeysf.write(encrypted_data)


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


# Check if encryption secret already exists
if Path(settings.ENCKEY_PATH).is_file():
    print("Encryption secret found.")
else:
    print("Encryption secret not found.")
    print("Generating secret...")
    newsecret = Fernet.generate_key()
    with open(settings.ENCKEY_PATH, "wb") as secret_file:
        secret_file.write(newsecret)
    print("Encryption secret generated and stored in {0}".format(settings.ENCKEY_PATH))


if __name__ == "__main__":
    start = ask_yn("Have you run this program as the correct user (for example, nginx uses www-data)? [y/n] ")
    if not start:
        print("Please run this as the correct user with: sudo su [user] -s /bin/sh -c 'python3 keygen.py'")

    else:
        # Decrypt the existing keyfile
        secret = load_secret()
        keyf = Fernet(secret)

        genkey = True
        uploadkeysp = Path("uploadkeys")
        if not uploadkeysp.is_file():
            uploadkeysp.touch()
        else:
            with open("uploadkeys", "rb") as ukf:
                # read the encrypted data
                encrypted_data = ukf.read()


        if genkey:
            if decrypt_uploadkeys():  # Decrypt the file
                N = 64  # Size of key
                key = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(N))
                print("Your new key is: " + str(key))  # Print key
                append_uploadkey(key)  # Save the new key to file unencrypted
                encrypt_uploadkeys()  # Encrypt the uploadkeys file
            else:
                print("Exiting.")
