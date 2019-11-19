import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render

from tickets.decorators import is_authenticated_and_passes_test
from tickets.forms import ReplyForm, TicketForm, UserForm
from tickets.models import Ticket

logger = logging.getLogger(__name__)


def home(request):
    return render(request, 'base.html', {})


def new_ticket(request):
    form = TicketForm(
        initial={
            'name': f'{request.user.first_name} {request.user.last_name}'
        }
    )
    return render(request, 'tickets/new-ticket.html', {'form': form})


def tickets_list(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = TicketForm(request.POST)
            if form.is_valid():
                ticket = form.save(commit=False)
                ticket.owner = request.user
                ticket.save()
                logger.debug(f'{ticket} created.')
                request.session['ticket-uuid'] = str(ticket.uuid)
                return redirect('ticket_submitted')

        else:
            try:
                if request.user.is_superuser:
                    tickets = Ticket.objects.all()
                else:
                    tickets = Ticket.objects.filter(owner=request.user)
            except:    # noqa: E722
                tickets = None

            return render(
                request,
                'tickets/tickets-list.html',
                {'tickets': tickets}
            )

    else:
        return render(request, 'tickets/tickets-list.html', {})


def ticket_submitted(request):
    try:
        logger.debug('Checking if there is a ticket uuid in session.')
        submitted_ticket_uuid = request.session['ticket-uuid']
        del request.session['ticket-uuid']
        ticket = Ticket.objects.get(uuid=submitted_ticket_uuid)
        logger.debug(f'{ticket} found.')
        return render(request, 'tickets/ticket-submitted.html', {'ticket': ticket})  # noqa: E501

    except KeyError:
        logger.exception('Unable to retrieve ticket UUID of newly created ticket from session')  # noqa: E501
        return redirect('home')

    except ObjectDoesNotExist:
        logger.exception(f'Ticket {submitted_ticket_uuid} not found')
        return redirect('home')


def ticket_ownership(request, uuid):
    try:
        logger.debug(f'Retrieving ticket {uuid}')
        ticket = Ticket.objects.get(uuid=uuid)
    except ObjectDoesNotExist:
        logger.exception(f'Ticket {uuid} not found')
        return False

    if ticket.owner == request.user or request.user.is_superuser:
        return True
    else:
        logger.debug(
            f'Ticket is owned by {ticket.email}, not {request.user.email}.'
        )
        return False


@is_authenticated_and_passes_test(ticket_ownership)
def ticket(request, uuid):
    try:
        ticket = Ticket.objects.get(uuid=uuid)
    except ObjectDoesNotExist:
        logger.exception(f'Ticket {uuid} not found.')
        raise Http404

    if request.method == 'GET':
        ctx = {'ticket': ticket}
        if not ticket.reply_set.all() and request.user.is_superuser:
            ctx['form'] = ReplyForm()

        return render(request, 'tickets/ticket.html', ctx)

    if request.method == 'POST':
        if not request.user.is_superuser:
            return HttpResponse('Unauthorized', status=401)

        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.owner = request.user
            reply.ticket = ticket
            reply.save()
            logger.debug(f'Reply for ticket {ticket.uuid} created')
            return redirect('ticket', ticket.uuid)
        else:
            return HttpResponse('Bad Request', status=400)


@login_required
def user_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(
                request,
                'Profile updated successfully!',
                extra_tags='profile-updated'
            )
            return redirect('user-profile')
        else:
            return HttpResponse('Bad Request', status=400)
    else:
        user_form = UserForm(instance=request.user)

    return render(request, 'profile/profile-home.html', {'user_form': user_form})  # noqa: E501
