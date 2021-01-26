#!/usr/bin/env python3
"""
imgupload.py

Flask application for processing images uploaded through POST requests.
"""


from flask import Flask, request, jsonify, render_template, redirect
from flask_api import status

import os
import re
import datetime
from pathlib import Path
from PIL import Image
import tempfile

import settings  # app settings (such as allowed extensions)
import functions  # custom functions

app = Flask(__name__)  # app is the app


def allowed_extension(testext):
    if testext.lower() in settings.ALLOWED_EXTENSIONS:
        return True
    return False


def log_savelog(key, ip, savedname):
    if settings.SAVELOG_KEYPREFIX > 0:
        with open(settings.SAVELOG, "a+") as slogf:
            slogf.write(f"[{datetime.datetime.now()}] {key[:settings.SAVELOG_KEYPREFIX]}: {ip} - {savedname}\n")
        os.chmod(settings.SAVELOG, settings.SAVELOG_CHMOD)
    else:
        with open(settings.SAVELOG, "a+") as slogf:
            slogf.write(f"[{datetime.datetime.now()}] {ip} - {savedname}\n")
        os.chmod(settings.SAVELOG, settings.SAVELOG_CHMOD)


@app.route("/upload", methods = ["GET"])
def upload_redirect():
    return render_template("upload.html", settings = settings)


@app.route("/api/v1/upload", methods = ["GET", "POST"])
def upload():
    print("Request method was POST!")

    with open("uploadkeys", "r") as keyfile:
        validkeys = keyfile.readlines()  # load valid keys
    validkeys = [x.strip("\n") for x in validkeys]  # remove newlines
    while "" in validkeys:
        validkeys.remove("")  # remove blank keys
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
                if not "imageName" in request.form.keys():  # if an image name wasn't provided
                    print(f"Generating file with extension {fext}")
                    fname = functions.generate_name() + fext  # generate file name
                    print(f"Generated name: {fname}")
                else:  # if a name was requested
                    fname = request.form["imageName"]  # get the requested image name
                    if len(fname) > 0:  # if the requested name isn't blank
                        print(f"Request imageName: {fname}")
                        if not fname.lower().endswith(fext.lower()):  # if requested name doesn't have the correct extension
                            fname += fext  # add the extension
                            print(f"Added extension; new filename: {fname}")
                    else:  # if the requested name is blank
                        print("Requested filename is blank!")
                        fname = functions.generate_name() + fext  # generate a valid filename
                        print(f"Generated name: {fname}")

                # if f:  # if the uploaded image exists
                # not sure why the above was added, but I'll keep it here just in case
                print("Uploaded image exists")

                if Path(os.path.join(settings.UPLOAD_FOLDER, fname)).is_file():
                    print("Requested filename already exists!")
                    return jsonify({'status': 'error', 'error': 'FILENAME_TAKEN'}), status.HTTP_409_CONFLICT

                with tempfile.TemporaryFile() as tmpf:
                    f.save(tmpf)  # save the image temporarily (before removing EXIF)

                    image = Image.open(tmpf)
                    data = list(image.getdata())
                    stripped = Image.new(image.mode, image.size)
                    stripped.putdata(data)
                    stripped.save(os.path.join(settings.UPLOAD_FOLDER, fname))  # save the image without EXIF

                    print(f"Saved to {fname}")

                url = settings.ROOTURL + fname  # construct the url to the image

                if settings.SAVELOG != "/dev/null":
                    print("Saving to savelog")
                    log_savelog(request.form["uploadKey"], request.remote_addr, fname)

                print("Returning json response")
                return jsonify({'status'        : 'success',
                                'url'           : url,          # ex. https://example.com/AbcD1234.png
                                'name'          : fname,        # filename
                                'uploadedName'  : f.filename,   # name that was uploaded
                                }), status.HTTP_201_CREATED
            # if the extension was invalid
            print("Uploaded extension is invalid!")
            return jsonify({'status': 'error', 'error': 'INVALID_EXTENSION'}), status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

        # if the key was not valid
        print("Key is invalid!")
        print(f"Request key: {request.form['uploadKey']}")
        return jsonify({'status': 'error', 'error': 'UNAUTHORIZED'}), status.HTTP_401_UNAUTHORIZED

    # if uploadKey was not found in request body
    print("No uploadKey found in request!")
    return jsonify({'status': 'error', 'error': 'UNAUTHORIZED'}), status.HTTP_401_UNAUTHORIZED

if __name__ == "__main__":
    print("Run with `flask` or a WSGI server!")
