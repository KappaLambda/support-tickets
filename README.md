# Support helpdesk ticketing system

Simple and easy to use support helpdesk ticketing system Django app that integrates with existing websites, enabling users to communicate with the service owners by raising tickets. Responses are presented in a forum-like interface, with issue resolution tracking.

## Table of contents

* [Requirements](#requirements)
* [Setup - Install](#setup---install)
  * [Create PostgreSQL Database](#create-postgresql-database)
* [Automated Setup](#automated-setup)
* [Run](#run)
* [SSL Certificate](#ssl-certificate)
* [Mailgun Setup](#mailgun-setup)
* [Setup Login with Facebook](#setup-login-with-facebook)
* [Demo](#demo)
* [License](#license)

## Requirements

* Ubuntu 16.04
* Python 3.6.2
* [Pyenv](https://github.com/pyenv/pyenv)
* [Pyenv virtualenv plugin](https://github.com/pyenv/pyenv-virtualenv)
* Nginx
* PostgreSQL

## Setup - Install

```bash
sudo apt-get update
sudo apt-get install -y libpq-dev postgresql postgresql-contrib nginx

# Pyenv prerequisites to avoid common build problems
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev python-openssl

# Pyenv-virtualenv repo clone and istallation
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bashrc
exec "$SHELL"
git clone https://github.com/pyenv/pyenv-virtualenv.git $(pyenv root)/plugins/pyenv-virtualenv
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
exec "$SHELL"

# Install python 3.6.2 with pyenv and create the python virtual environment
pyenv install 3.6.2
pyenv virtualenv 3.6.2 support_tickets

# Clone repo and install requirements
git clone https://github.com/KappaLambda/support-tickets.git /srv/www/support-tickets/
cd /srv/www/support-tickets/
pyenv local support_tickets
pip install -r requirements.txt

# Copy nginx block and restart Nginx service
sudo ln -s /srv/www/support-tickets/nginx-blocks/support.liopetas.com.conf /etc/nginx/sites-enabled/support.liopetas.com.conf
sudo nginx -t && sudo service nginx restart
```

### Create PostgreSQL Database

Log in directly into Postgres

```bash
sudo -u postgres psql
```

then on Postgres session

```sql
postgres=# CREATE DATABASE support;
postgres=# CREATE USER liopetas_support WITH PASSWORD 'password';
postgres=# ALTER ROLE liopetas_support SET client_encoding TO 'utf8';
postgres=# ALTER ROLE liopetas_support SET default_transaction_isolation TO 'read committed';
postgres=# ALTER ROLE liopetas_support SET timezone TO 'UTC';
postgres=# GRANT ALL PRIVILEGES ON DATABASE support TO liopetas_support;
postgres=# \q.
```

## Automated Setup

### Requirements for automated setup

* [Vagrant](https://www.vagrantup.com/)
* [Virtualbox](https://www.virtualbox.org/)

Install latest versions of Vagrant and VirtualBox.

Inside repo's root directory there is a `Vagrantfile` that can be used to bring up a virtual machine.

There is also a provision script, `vagrant_setup.sh` that installs all prerequisites and requirements, installs pyenv and virtualenv, creates the database, clones the repo, applies migrations, creates simlink for nginx block, etc.

In this case the above [setup](#setup---install) procedure is not needed.

Clone repo or copy the important files (`Vagrantfile`, `vagrant_setup.sh`, `bash_local`) and then just run the following commands to bring up the VM:

```bash
export SUPPORT_DATABASE_PASSWORD="password"
# bring up the VM
vagrant up
```

## Run

If you didn't follow the automated setup.

```bash
export SUPPORT_DATABASE_PASSWORD="password"
cd /srv/www/support-tickets/support_tickets/
python manage.py migrate
python manage.py collectstatic --noinput
cd /srv/www/support-tickets/
bash gunicorn.sh
```

If you followed the automated setup.

```bash
# Log in to Virtual Machine
vagrant ssh
export SUPPORT_DATABASE_PASSWORD="password"
cd /srv/www/support-tickets/
bash gunicorn.sh
```

**Note:** You'll still need to issue the SSL Certificate. Check [below](#ssl-certificate).

## SSL Certificate

For SSL Certificate I used [dehydrated](https://github.com/lukas2511/dehydrated) and this [custom hook for CloudFlare](https://github.com/kappataumu/letsencrypt-cloudflare-hook) that enables the use of DNS records instead of a web server to complete the whole process and request a certificate from [Let's Encrypt](https://letsencrypt.org/). For more info and auto-renewal, read [this blog post](https://kappataumu.com/articles/letsencrypt-cloudflare-dns-01-hook.html).

For better security the entire certificate renewal proccess is running using the root account and certificates will be owned by root.

Below are the steps:

```bash
cd
sudo -s
mkdir ssl-certs
cd /ssl-certs/
git clone https://github.com/lukas2511/dehydrated.git
cd dehydrated/
mkdir hooks
git clone https://github.com/kappataumu/letsencrypt-cloudflare-hook hooks/cloudflare
pyenv virtualenv 3.7.0 letsencrypt
pyenv local letsencrypt
pip install -r hooks/cloudflare/requirements.txt
export CF_EMAIL='user@example.com'  # Change this to your Cloudflare account email
export CF_KEY='K9uX2HyUjeWg5AhAb'  # Change this to your Cloudflare API key
./dehydrated --register --accept-terms
./dehydrated -c -d support.liopetas.com -t dns-01 -k 'hooks/cloudflare/hook.py'
```

To generate dhparam.pem

```bash
sudo openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048
```

## Mailgun Setup

The app uses [Mailgun](https://www.mailgun.com/) to send notification emails for new issues. You'll need to edit `mailgun.conf` with your `MAILGUN_DOMAIN_NAME` and `MAILGUN_API_KEY`.

## Setup Login with Facebook

`Login with Facebook` requires you to have an account on [Facebook for Developers](https://developers.facebook.com/), create an App and activate the Facebook Login Product. Facebook API version for this application should be `v5.0`.

After that, you need to login to Django Admin and do the following.

1. Change site `example.com` in Sites to `https://support.liopetas.com`.
2. Create a Social Application with provider `Facebook` and put the `App ID` and `App secret` from the application you created in Facebook for Developers.

## Demo

You can see a demo [here](https://support.liopetas.com).

## License

[The MIT License](LICENSE.md)
