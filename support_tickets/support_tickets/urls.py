from django.conf.urls import include, url
from django.contrib import admin

from tickets import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^tickets/new/$', views.new_ticket, name='new_ticket'),
    url(
        r'^tickets/([a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12})/$',
        views.ticket,
        name='ticket'
    ),
    url(r'^tickets/$', views.tickets_list, name='tickets_list'),
    url(r'^tickets/submitted/$', views.ticket_submitted, name='ticket_submitted'),  # noqa: E501
    url(r'^accounts/', include('allauth.urls')),
    url(r'^account/profile/$', views.user_profile, name='user-profile'),
    url(r'^admin/', admin.site.urls),
]
