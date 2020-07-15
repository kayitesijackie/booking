from django.http import HttpResponse
from django.views.generic import View
from project.utils import render_to_pdf 
from booking.views import bus_details
from booking.models import Ticket


def generate_view(request, payment):

    gotten_ticket = Ticket.get_single_ticket(payment)

    pdf = render_to_pdf('pdf/ticket.html', {'gotten_ticket':gotten_ticket})

    if pdf:

        response = HttpResponse(pdf, content_type='application/pdf')

        filename = "Ticket_%s.pdf" %(gotten_ticket.ticket_number)

        content = "inline; filename='%s'"%(filename)

        download = request.GET.get("download")

        if download:

            content = "attachment; filename='%s'"%(filename)

        response['Content-Disposition'] = content

        return response

    return HttpResponse('Not Found')