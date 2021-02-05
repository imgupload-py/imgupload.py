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
import logging

import settings  # app settings (such as allowed extensions)
import functions  # custom functions


logging.basicConfig(level=settings.LOGLEVEL)
logger = logging.getLogger("app")
logger.info("Initialized logging")

import util


app = Flask(__name__)  # app is the app


@app.route("/upload", methods = ["GET"])
def upload_redirect():
    logger.info("Received GET /upload, returning template")
    return render_template("upload.html", settings = settings)


@app.route("/api/v1/upload", methods = ["POST"])
def upload():
    logger.info("Received POST /api/v1/upload")
    validkeys = util.load_uploadkeys()
    logger.debug("Loaded validkeys")

    if not "uploadKey" in request.form:  # if an uploadKey wasn't provided
        logger.info("No uploadKey found in request!")
        return jsonify({'status': 'error', 'error': 'UNAUTHORIZED'}), status.HTTP_401_UNAUTHORIZED

    if not request.form["uploadKey"] in validkeys:  # if uploadKey is invalid
        logger.info("Key is invalid!")
        logger.debug(f"Request key: {request.form['uploadKey']}")
        return jsonify({'status': 'error', 'error': 'UNAUTHORIZED'}), status.HTTP_401_UNAUTHORIZED

    logger.info("Key is valid!")

    if "verify" in request.form.keys():
        if request.form["verify"] == "true":
            logger.info("Request is asking if key is valid (it is)")
            return jsonify({'status': 'key_valid'})

    if not "imageUpload" in request.files:  # if the image to upload wasn't provided
        logger.info("No image upload was found!")
        return jsonify({'status': 'error', 'error': 'NO_IMAGE_UPLOADED'}), status.HTTP_400_BAD_REQUEST

    f = request.files["imageUpload"]  # f is the image to upload

    if f.filename == "":  # if the filename is blank (possibly no image uploaded)
        logger.info("Filename is blank")
        return jsonify({'status': 'error', 'error': 'FILENAME_BLANK'}), status.HTTP_400_BAD_REQUEST

    fext = Path(f.filename).suffix  # get the uploaded extension
    if not fext.lower() in settings.ALLOWED_EXTENSIONS:  # if the extension isn't allowed
        logger.info("Uploaded extension is invalid!")
        return jsonify({'status': 'error', 'error': 'INVALID_EXTENSION'}), status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

    if not "imageName" in request.form.keys():  # if an image name wasn't provided
        fname = functions.generate_name() + fext  # generate file name
        logger.info(f"Generated name: {fname}")
    else:  # if a name was requested
        fname_unsafe = request.form["imageName"]  # get the requested image name
        logger.debug(f"Request imageName: {fname_unsafe}")
        fname = secure_filename(fname_unsafe)  # sanitize the image name
        logger.info(f"Sanitized imageName: {fname}")
        if len(fname) <= 0:  # if the requested name is blank
            logger.info("Requested filename is blank!")
            return jsonify({'status': 'error', 'error': 'REQUESTED_FILENAME_BLANK'}), status.HTTP_400_BAD_REQUEST
        if not fname.lower().endswith(fext.lower()):  # if requested name doesn't have the correct extension
            fname += fext  # add the extension
            logger.info(f"Added extension; new filename: {fname}")

    # if f:  # if the uploaded image exists
    # not sure why the above was added, but I'll keep it here just in case

    if Path(os.path.join(settings.UPLOAD_FOLDER, fname)).is_file():
        logger.info("Requested filename already exists!")
        return jsonify({'status': 'error', 'error': 'FILENAME_TAKEN'}), status.HTTP_409_CONFLICT

    util.save_and_strip_exif(f, fname)
    logger.info(f"Saved to {fname}")

    url = settings.ROOTURL + fname  # construct the url to the image

    if settings.SAVELOG != "/dev/null":
        logger.info("Logging to savelog")
        util.log_savelog(request.form["uploadKey"], request.remote_addr, fname)

    logger.info("Returning json response")
    return jsonify({'status'        : 'success',
                    'url'           : url,          # ex. https://example.com/AbcD1234.png
                    'name'          : fname,        # filename on server
                    'sourceName'    : f.filename,   # original filename
                    }), status.HTTP_201_CREATED

if __name__ == "__main__":
    app.run(host="127.0.0.1", port="5001", debug=True)
