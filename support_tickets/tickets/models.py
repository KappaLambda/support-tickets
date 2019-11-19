import uuid

from django.contrib.auth.models import User
from django.db import models


class Ticket(models.Model):

    ISSUE_CHOICES = (
        (0, 'Other'),
        (1, 'Issue 1'),
        (2, 'Issue 2'),
        (3, 'Issue 3'),
        (4, 'Issue 4'),
    )

    SEVERITY_CHOICES = (
        (0, 'Low'),
        (1, 'Medium'),
        (2, 'High'),
        (3, 'Critical'),
    )

    issue = models.IntegerField(choices=ISSUE_CHOICES, verbose_name='issue')
    description = models.TextField(verbose_name='description')

    severity = models.IntegerField(
        choices=SEVERITY_CHOICES,
        verbose_name='severity',
    )

    issue_submit_date = models.DateTimeField(
        auto_now=True,
        verbose_name='date submitted',
    )

    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        verbose_name='ticket UUID',
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='ticket owner',
    )

    def __str__(self):
        return f'Ticket {self.uuid}'


class Reply(models.Model):

    date = models.DateTimeField(auto_now=True, verbose_name='date')
    answer = models.TextField(verbose_name='answer')

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='owner',
    )

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        verbose_name='ticket',
    )

    def __str__(self):
        return f'Reply {self.id}'


class UserProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='user'
    )
