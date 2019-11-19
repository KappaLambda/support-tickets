from django.contrib import admin

from .models import Reply, Ticket, UserProfile


class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'uuid',
        'email',
        'full_name',
        'issue',
        'severity',
        'issue_submit_date',
    )

    readonly_fields = (
        'id',
        'uuid',
        'issue_submit_date',
        'email',
        'owner',
        'full_name',
    )

    fieldsets = (
        (
            'Editable info',
            {
                'fields': (
                    'issue',
                    'severity',
                    'description',
                )
            },
        ),
        (
            'Non-Editable info',
            {
                'fields': (
                    'id',
                    'uuid',
                    'issue_submit_date',
                    'email',
                    'owner',
                    'full_name',
                )
            },
        ),
    )

    def full_name(self, instance):
        return f'{instance.owner.first_name} {instance.owner.last_name}'

    def email(self, instance):
        return instance.owner.email


class ReplyAdmin(admin.ModelAdmin):
    list_display = (
        'owner',
        'answer',
        'date',
        'ticket',
        'ticket_email',
    )

    readonly_fields = (
        'owner',
        'date',
        'ticket',
        'ticket_email',
    )

    fieldsets = (
        (
            'Editable info',
            {
                'fields': (
                    'answer',
                )
            },
        ),
        (
            'Non-Editable info',
            {
                'fields': (
                    'owner',
                    'date',
                    'ticket',
                    'ticket_email',
                )
            },
        ),
    )

    def ticket_email(self, obj):
        return obj.ticket.email


class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'first_name',
        'last_name',
    )

    readonly_fields = (
        'user',
        'first_name',
        'last_name',
    )

    fieldsets = (
        (
            'Non-Editable info',
            {
                'fields': (
                    'user',
                    'first_name',
                    'last_name',
                )
            },
        ),
    )

    def first_name(self, instance):
        return instance.user.first_name

    def last_name(self, instance):
        return instance.user.last_name


admin.site.register(Ticket, TicketAdmin)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
