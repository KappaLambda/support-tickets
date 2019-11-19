import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'support_tickets.settings.prod')  # noqa: E501

application = get_wsgi_application()
