# imgupload

<!---![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/BBaoVanC/imgupload/master?color=purple)
![GitHub repo size](https://img.shields.io/github/repo-size/bbaovanc/imgupload?color=purple)
![GitHub All Releases](https://img.shields.io/github/downloads/bbaovanc/imgupload/total?color=purple)
![GitHub issues](https://img.shields.io/github/issues/bbaovanc/imgupload?color=purple)
![GitHub closed issues](https://img.shields.io/github/issues-closed/bbaovanc/imgupload?color=purple)
![GitHub](https://img.shields.io/github/license/bbaovanc/imgupload?color=purple)-->

## What is imgupload?

imgupload is a Flask + uWSGI application to serve as an all-purpose image/file uploader over POST requests.

---

## FAQ

**Where can I send bug reports and feature requests?**

You can create an issue [here](https://git.bbaovanc.com/bbaovanc/imgupload/issues).

**How do I use this program?**

See [Installation](#installation)

**I want to make a pull request. Where should I do that?**

First, fork [this repository](https://git.bbaovanc.com/bbaovanc/imgupload). If you don't have an account on my Gitea site yet, you can either create one, or sign in using your GitHub account. Commit your changes to your fork, and then create a pull request.

---

## Installation

### Using uWSGI

Note: replace `www-data` with whatever user your webserver runs as.

1. Make /srv/imgupload: `sudo mkdir /srv/imgupload`
2. Change ownership of /srv/imgupload: `sudo chown www-data:www-data /srv/imgupload`
3. Enter www-data user: `sudo su www-data`
4. Change directories to /srv/imgupload: `cd /srv/imgupload`
5. Clone the repository: `git clone https://git.bbaovanc.com/bbaovanc/imgupload.git`
6. Checkout the version you want (replace [version] with desired version: `git checkout [version]`
7. Enter the imgupload directory: `cd imgupload`
8. Create a virtualenv: `python3 -m venv env`
9. Enter the virtualenv: `source env/bin/activate`
10. Install dependencies: `python3 -m pip install -r requirements.txt`
11. Leave the www-data user: `exit`
12. Copy the default uWSGI configuration: `sudo cp /srv/imgupload/uwsgi.ini.default /etc/uwsgi/apps-available/imgupload.ini`
13. Modify `/etc/uwsgi/apps-available/imgupload.ini` to your preferences
14. Enable imgupload: `sudo ln -s /etc/uwsgi/apps-available/imgupload.ini /etc/uwsgi/apps-enabled/`
15. Restart uWSGI: `sudo systemctl restart uwsgi`
16. Set up your webserver to proxy the uwsgi.sock

Example NGINX location block:

```nginx
location /upload {
    include uwsgi_params;
    uwsgi_pass unix:/srv/imgupload/uwsgi.sock;
    client_max_body_size 25M;
}
```

### Using Flask development server

#### Setup

```shell
git clone https://git.bbaovanc.com/bbaovanc/imgupload.git
cd imgupload
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```

#### Run

```shell
export FLASK_APP=imgupload.py
flask run
```

---

## License

_imgupload_ is licensed under the GPLv3 license. For more information, please refer to [`LICENSE`](https://git.bbaovanc.com/bbaovanc/imgupload/src/branch/master/LICENSE)
