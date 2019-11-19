#!/usr/bin/env bash
set -euxo pipefail

if [[ -z "${SUPPORT_DATABASE_PASSWORD}" ]]; then
    echo "Set SUPPORT_DATABASE_PASSWORD env to run provision script."
    exit
else
    echo "Starting provision."
    echo "-----------------------------"
    start_seconds="$(date +%s)"
fi

apt_packages=(
    vim
    curl
    wget
    git

    # pyenv requirements from common build issues
    make
    build-essential
    libssl-dev
    zlib1g-dev
    libbz2-dev
    libreadline-dev
    libsqlite3-dev
    llvm
    libncurses5-dev
    libncursesw5-dev
    xz-utils
    tk-dev
    libffi-dev
    liblzma-dev
    python-openssl

    # psycopg2 requirements. More info here: https://github.com/psycopg/psycopg2/issues/560
    libpq-dev
    python-dev

    # project needed packages
    postgresql
    postgresql-contrib
    nginx
)

sudo apt-get update -y
# Force debconf frontend to noninteractive and set option to package manager to install new conf without prompt.
sudo DEBIAN_FRONTEND=noninteractive apt-get -o Dpkg::Options::="--force-confnew" -y upgrade

# Packages Installation
echo "Installing packages..."
sudo apt-get install -y ${apt_packages[@]}
sudo apt-get clean

# pyenv installation
if [ ! -d "/home/vagrant/.pyenv" ]; then
    echo "Installing pyenv and virtualenv plugin"
    git clone https://github.com/pyenv/pyenv.git /home/vagrant/.pyenv
    git clone https://github.com/pyenv/pyenv-virtualenv.git /home/vagrant/.pyenv/plugins/pyenv-virtualenv
else
    echo "Pyenv is already installed."
fi

# Check if we can run pyenv command
if command -v pyenv; then
    pyenv version
else
    echo "Setting Pyenv variables"
    export PYENV_ROOT="/home/vagrant/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
    # Set PROMPT_COMMAND="" to empty until PR #248, https://github.com/pyenv/pyenv-virtualenv/pull/248 is merged.
    PROMPT_COMMAND="" eval "$(pyenv virtualenv-init -)"
fi

# Install python 3.6.2 with pyenv, delete virtual env and recreate it.
pyenv install 3.6.2 --skip-existing

#  Check if project virtualenv exists or create it
if [ ! -d "/home/vagrant/.pyenv/versions/3.6.2/envs/support_tickets" ]; then
    pyenv virtualenv 3.6.2 support_tickets
fi

# Create PostgreSQL Database for support tickets helpdesk
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw support; then
    echo "PostgreSQL database exists. Skipping setup."
else
    echo "Creating PostgreSQL database for production."
    sudo -u postgres psql -c "CREATE DATABASE support"
    sudo -u postgres psql -c "CREATE USER liopetas_support WITH PASSWORD '$SUPPORT_DATABASE_PASSWORD'"
    sudo -u postgres psql -c "ALTER ROLE liopetas_support SET client_encoding TO 'utf8'"
    sudo -u postgres psql -c "ALTER ROLE liopetas_support SET default_transaction_isolation TO 'read committed'"
    sudo -u postgres psql -c "ALTER ROLE liopetas_support SET timezone TO 'UTC'"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE support TO liopetas_support"
fi

# Preemptively accept Github's SSH fingerprint, but only
# if we previously haven't done so.
fingerprint="$(ssh-keyscan -H github.com)"
if ! grep -qs "$fingerprint" /home/vagrant/.ssh/known_hosts; then
    echo "$fingerprint" >> /home/vagrant/.ssh/known_hosts
    echo "Added github.com fingerprint"
fi

# Vagrant should've created /srv/www according to the Vagrantfile,
# but let's make sure it exists even if run directly.
if [[ ! -d "/srv/www" ]]; then
    echo "Creating /srv/www/"
    sudo mkdir "/srv/www"
    sudo chown vagrant:vagrant "/srv/www"
fi

# Check if repo directory exists, if not clone repo
if [[ ! -d "/srv/www/support-tickets" ]]; then
    echo "Cloning repo, setting virtual environment and installing requirements."
    git clone git@github.com:KappaLambda/support-tickets.git /srv/www/support-tickets/
    cd /srv/www/support-tickets/
    pyenv local support_tickets
    pip install -r requirements.txt
    cd /srv/www/support-tickets/support_tickets/
    python manage.py migrate
    python manage.py collectstatic --noinput
fi

# set nginx
if [ ! -h "/etc/nginx/sites-enabled/support.liopetas.com.conf" ] && [[ -d "/srv/www/support-tickets" ]]; then
    echo "Creating Nginx block symlink."
    sudo ln -s /srv/www/support-tickets/nginx-blocks/support.liopetas.com.conf /etc/nginx/sites-enabled/support.liopetas.com.conf
    sudo nginx -t && sudo service nginx restart
fi

# Check .bashrc sources .bash_local
if ! grep -qs "source /home/vagrant/.bash_local" /home/vagrant/.bashrc; then
    echo "Source .bash_local in .bashrc"
    echo "source /home/vagrant/.bash_local" >> /home/vagrant/.bashrc
    source /home/vagrant/.bashrc
fi

end_seconds="$(date +%s)"
echo "-----------------------------"
echo "Provision completed in "$(expr $end_seconds - $start_seconds)" seconds"
