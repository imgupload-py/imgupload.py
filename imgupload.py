#!/usr/bin/env python3
"""
imgupload.py

Flask application for processing images uploaded through POST requests.
"""

from flask import Flask, request, jsonify, Response
from flask_api import status
from pathlib import Path
import os
import datetime

import settings  # app settings (such as allowed extensions)
import functions  # custom functions

app = Flask(__name__)  # app is the app


def allowed_extension(testext):
    if testext.lower() in settings.ALLOWED_EXTENSIONS:
        return True
    else:
        return False


def log_savelog(key, ip, savedname):
    if settings.SAVELOG_KEYPREFIX > 0:
        with open(settings.SAVELOG, "a+") as slogf:
            slogf.write("[{0}] {1}: {2} - {3}\n".format(datetime.datetime.now(), key[:settings.SAVELOG_KEYPREFIX], ip, savedname))
        os.chmod(settings.SAVELOG, settings.SAVELOG_CHMOD)
    else:
        with open(settings.SAVELOG, "a+") as slogf:
            slogf.write("[{0}] {1} - {2}\n".format(datetime.datetime.now(), ip, savedname))
        os.chmod(settings.SAVELOG, settings.SAVELOG_CHMOD)

@app.route("/upload", methods = ["POST"])
def upload():
    if request.method == "POST":  # sanity check: make sure it's a POST request
        print("Request method was POST!")

        with open("uploadkeys", "r") as keyfile:  # load valid keys
            validkeys = keyfile.readlines()
        validkeys = [x.strip("\n") for x in validkeys]
        while "" in validkeys:
            validkeys.remove("")
        print("Loaded validkeys")

        if "uploadKey" in request.form:  # if an uploadKey was provided
            if request.form["uploadKey"] in validkeys:  # check if uploadKey is valid
                print("Key is valid!")

                if "verify" in request.form.keys():
                    if request.form["verify"] == "true":
                        print("Request is asking if key is valid (it is)")
                        return jsonify({'status': 'key_valid'})

                if "imageUpload" in request.files:  # check if image to upload was provided
                    f = request.files["imageUpload"]  # f is the image to upload
                else:
                    print("No image upload was found!")
                    return jsonify({'status': 'error', 'error': 'NO_IMAGE_UPLOADED'}), status.HTTP_400_BAD_REQUEST

                if f.filename == "":  # make sure the filename isn't blank
                    print("Filename is blank")
                    return jsonify({'status': 'error', 'error': 'FILENAME_BLANK'}), status.HTTP_400_BAD_REQUEST

                fext = Path(f.filename).suffix  # get the uploaded extension
                if allowed_extension(fext):  # if the extension is allowed
                    print("Generating file with extension {0}".format(fext))
                    fname = functions.generate_name() + fext  # generate file name
                    print("Generated name: {0}".format(fname))

                    if f:  # if the uploaded image exists
                        print("Uploaded image exists")
                        if Path(os.path.join(settings.UPLOAD_FOLDER, fname)).is_file():
                            print("Requested filename already exists!")
                            return jsonify({'status': 'error', 'error': 'FILENAME_TAKEN'}), status.HTTP_409_CONFLICT
                        f.save(os.path.join(settings.UPLOAD_FOLDER, fname))  # save the image
                        print("Saved to {0}".format(fname))
                        url = settings.ROOTURL + fname  # construct the url to the image
                        if settings.SAVELOG != "/dev/null":
                            print("Saving to savelog")
                            log_savelog(request.form["uploadKey"], request.remote_addr, fname)
                        print("Returning json response")
                        return jsonify({'status': 'success', 'url': url, 'name': fname, 'uploadedName': f.filename}), status.HTTP_201_CREATED
                    else:  # this shouldn't happen
                        print("Um... uploaded image... is nonexistent? Please report this error!")
                        return jsonify({'status': 'error', 'error': 'UPLOADED_IMAGE_FAILED_SANITY_CHECK_1'}), status.HTTP_400_BAD_REQUEST

                else:  # if the extension was invalid
                    print("Uploaded extension is invalid!")
                    return jsonify({'status': 'error', 'error': 'INVALID_EXTENSION'}), status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

            else:  # if the key was not valid
                print("Key is invalid!")
                print("Request key: {0}".format(request.form["uploadKey"]))
                return jsonify({'status': 'error', 'error': 'UNAUTHORIZED'}), status.HTTP_401_UNAUTHORIZED

        else:  # if uploadKey was not found in request body
            print("No uploadKey found in request!")
            return jsonify({'status': 'error', 'error': 'UNAUTHORIZED'}), status.HTTP_401_UNAUTHORIZED

if __name__ == "__main__":
    print("Run with `flask` or a WSGI server!")
