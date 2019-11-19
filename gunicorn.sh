#!/bin/bash

if [ $HOSTNAME == "vagrant" ]
then
    export DJANGO_SETTINGS_MODULE="support_tickets.settings.develop"
    echo "Set Django to developemnt settings"
fi

$(pyenv which gunicorn) \
    --reload \
    --timeout 30 \
    --chdir ./support_tickets/ \
    --access-logfile - \
    --workers 3 \
    --bind unix:/tmp/support_tickets.sock \
    support_tickets.wsgi:application
