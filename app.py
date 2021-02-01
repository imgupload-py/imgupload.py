#!/usr/bin/env python3
"""
imgupload.py

Flask application for processing images uploaded through POST requests.
"""


from flask import Flask, request, jsonify, render_template
from flask_api import status
from werkzeug.utils import secure_filename

import os
from pathlib import Path
from PIL import Image
import tempfile

import util

import settings  # app settings (such as allowed extensions)
import functions  # custom functions

app = Flask(__name__)  # app is the app


@app.route("/upload", methods = ["GET"])
def upload_redirect():
    return render_template("upload.html", settings = settings)


@app.route("/api/v1/upload", methods = ["GET", "POST"])
def upload():
    print("Request method was POST!")

    validkeys = util.load_uploadkeys()
    print("Loaded validkeys")

    if not "uploadKey" in request.form:  # if an uploadKey wasn't provided
        print("No uploadKey found in request!")
        return jsonify({'status': 'error', 'error': 'UNAUTHORIZED'}), status.HTTP_401_UNAUTHORIZED

    if not request.form["uploadKey"] in validkeys:  # if uploadKey is invalid
        print("Key is invalid!")
        print(f"Request key: {request.form['uploadKey']}")
        return jsonify({'status': 'error', 'error': 'UNAUTHORIZED'}), status.HTTP_401_UNAUTHORIZED

    print("Key is valid!")

    if "verify" in request.form.keys():
        if request.form["verify"] == "true":
            print("Request is asking if key is valid (it is)")
            return jsonify({'status': 'key_valid'})

    if not "imageUpload" in request.files:  # if the image to upload wasn't provided
        print("No image upload was found!")
        return jsonify({'status': 'error', 'error': 'NO_IMAGE_UPLOADED'}), status.HTTP_400_BAD_REQUEST

    f = request.files["imageUpload"]  # f is the image to upload

    if f.filename == "":  # if the filename is blank (possibly no image uploaded)
        print("Filename is blank")
        return jsonify({'status': 'error', 'error': 'FILENAME_BLANK'}), status.HTTP_400_BAD_REQUEST

    fext = Path(f.filename).suffix  # get the uploaded extension
    if not fext.lower() in settings.ALLOWED_EXTENSIONS:  # if the extension isn't allowed
        print("Uploaded extension is invalid!")
        return jsonify({'status': 'error', 'error': 'INVALID_EXTENSION'}), status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

    if not "imageName" in request.form.keys():  # if an image name wasn't provided
        print(f"Generating file with extension {fext}")
        fname = functions.generate_name() + fext  # generate file name
        print(f"Generated name: {fname}")
    else:  # if a name was requested
        fname_unsafe = request.form["imageName"]  # get the requested image name
        print(f"Request imageName: {fname_unsafe}")
        fname = secure_filename(fname_unsafe)  # sanitize the image name
        print(f"Sanitized imageName: {fname}")
        if len(fname) <= 0:  # if the requested name is blank
            print("Requested filename is blank!")
            return jsonify({'status': 'error', 'error': 'REQUESTED_FILENAME_BLANK'}), status.HTTP_400_BAD_REQUEST
        if not fname.lower().endswith(fext.lower()):  # if requested name doesn't have the correct extension
            fname += fext  # add the extension
            print(f"Added extension; new filename: {fname}")

    # if f:  # if the uploaded image exists
    # not sure why the above was added, but I'll keep it here just in case
    print("Uploaded image exists")

    if Path(os.path.join(settings.UPLOAD_FOLDER, fname)).is_file():
        print("Requested filename already exists!")
        return jsonify({'status': 'error', 'error': 'FILENAME_TAKEN'}), status.HTTP_409_CONFLICT

    util.save_and_strip_exif(f, fname)
    print(f"Saved to {fname}")

    url = settings.ROOTURL + fname  # construct the url to the image

    if settings.SAVELOG != "/dev/null":
        print("Saving to savelog")
        util.log_savelog(request.form["uploadKey"], request.remote_addr, fname)

    print("Returning json response")
    return jsonify({'status'        : 'success',
                    'url'           : url,          # ex. https://example.com/AbcD1234.png
                    'name'          : fname,        # filename on server
                    'sourceName'    : f.filename,   # original filename
                    }), status.HTTP_201_CREATED

if __name__ == "__main__":
    print("Run with `flask` or a WSGI server!")
