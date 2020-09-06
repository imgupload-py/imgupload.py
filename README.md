# imgupload

![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/BBaoVanC/imgupload/master?color=purple)
![GitHub repo size](https://img.shields.io/github/repo-size/bbaovanc/imgupload?color=purple)
![GitHub All Releases](https://img.shields.io/github/downloads/bbaovanc/imgupload/total?color=purple)
![GitHub issues](https://img.shields.io/github/issues/bbaovanc/imgupload?color=purple)
![GitHub closed issues](https://img.shields.io/github/issues-closed/bbaovanc/imgupload?color=purple)
![GitHub](https://img.shields.io/github/license/bbaovanc/imgupload?color=purple)

## What is imgupload?

imgupload is a Flask + uWSGI application to serve as an all-purpose image/file uploader over POST requests.

---

## FAQ

**Where can I send bug reports and feature requests?**

You can create an issue [here](https://gitea.bbaovanc.com/bbaovanc/imgupload/issues).

**How do I use this program?**

See [Installation](#installation)

**I want to make a pull request. Where should I do that?**

First, fork [this repository](https://gitea.bbaovanc.com/bbaovanc/imgupload). If you don't have an account on my Gitea site yet, you can either create one, or sign in using your GitHub account. Commit your changes to your fork, and then create a pull request.

---

## Installation

1. Clone the repository: `git clone https://gitea.bbaovanc.com/bbaovanc/imgupload.git`
2. Enter the imgupload directory: `cd imgupload`
3. Create a virtualenv: `python3 -m venv env`
4. Enter the virtualenv: `source env/bin/activate`
5. Install dependencies: `python3 -m pip install -r requirements.txt`
6. [Run the Flask app](#running-the-flask-App)

---

## Running the Flask app

### Using uWSGI

[https://uwsgi-docs.readthedocs.io/en/latest/Configuration.html](https://uwsgi-docs.readthedocs.io/en/latest/Configuration.html)

Instructions specific to imgupload are coming soon

### Using Flask development server

```shell
$ source env/bin/activate  # if you haven't already entered the virtualenv
$ export FLASK_APP=imgupload.py
$ flask run
```

---

## License

_imgupload_ is licensed under the GPLv3 license. For more information, please refer to [`LICENSE`](https://gitea.bbaovanc.com/bbaovanc/imgupload/src/branch/master/LICENSE)
