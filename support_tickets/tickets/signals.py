import json
import logging
import os

import requests
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Ticket, UserProfile

logger = logging.getLogger(__name__)


def _get_mailgun_settings():
    mailgun_conf_path = os.path.abspath(os.path.join(__file__, '../../..'))
    mailgun_conf_file = os.path.join(mailgun_conf_path, 'mailgun.conf')
    try:
        with open(mailgun_conf_file) as mailgun_json:
            mailgun_conf = json.load(mailgun_json)
            return mailgun_conf

    except FileNotFoundError:
        logger.exception(
            'File "mailgun.conf" does not exist!\n'
            'Here is the exception message:'
        )
        return None


def _send_mailgun_email(data, email, ticket, mailgun_settings):
    try:
        data['to'] = email
        response = requests.post(
            f'https://api.mailgun.net/v3/{mailgun_settings["DOMAIN_NAME"]}/messages',  # noqa: E501
            auth=('api', mailgun_settings['MAILGUN_API_KEY']),
            data=data
        )
        json_data = json.loads(response.text)
    except Exception:
        logger.exception()
        return False

    if response.status_code == requests.codes.ok:
        logger.debug(
            f'Email "{json_data.get("id", "")}" sent to {data["to"]}.'
        )
    else:
        logger.error(
            f'Email request status {response.status_code}, '
            f'email message: "{json_data.get("message", "")}"'
        )
        return False

    return json_data.get('id', '')


@receiver(post_save, sender=Ticket)
def send_email_notification(sender, **kwargs):
    ticket = kwargs.get('instance')
    mailgun_settings = _get_mailgun_settings()
    if not mailgun_settings:
        return None

    data = {
        'from': (
            f'Support Tickets <postmaster@{mailgun_settings["DOMAIN_NAME"]}>'
        ),
        'subject': f'Ticket #{ticket.id}',
        'text': (
            f'Ticket issue: {ticket.issue}\n'
            f'Issue severity: {ticket.severity}\n'
            f'Date submitted: {ticket.issue_submit_date}\n\n'
            f'Description:\n{ticket.description}\n\n'
            f'For more information: https://support.liopetas.com/tickets/{ticket.uuid}/'  # noqa: E501
        ),
    }

    recipients = [ticket.owner.email, 'liopetas.kostas@gmail.com']
    return [_send_mailgun_email(data, email, ticket, mailgun_settings) for email in recipients]  # noqa: E501


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        logger.debug(f'Profile for {instance} created.')
