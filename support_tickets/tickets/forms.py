from django import forms
from django.contrib.auth.models import User

from .models import Reply, Ticket


class TicketForm(forms.ModelForm):

    class Meta:
        model = Ticket
        fields = [
            'issue',
            'severity',
            'description',
        ]


class ReplyForm(forms.ModelForm):

    class Meta:
        model = Reply
        fields = ['answer']


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
        ]
