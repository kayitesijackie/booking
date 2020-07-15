from django.shortcuts import render, redirect
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from .models import BusOrganisation, Route, Bus, Schedule, Ticket, PaymentForm
from datetime import datetime, date
from .forms import TicketForm, Payment
import uuid
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.generic import View
from project.utils import render_to_pdf 
# from booking.views import bus_details
# from booking.models import Ticket


import phonenumbers
from decouple import config
import requests
import random



def home(request):
    '''
    view function for landing page
    '''
    return render(request, 'home.html')

# def schedule(request):
#     '''
#     view function for schedules page
#     '''
#     schedule = Schedule.objects.all()
#     return render(request,'schedule.html',{'schedule':schedule})

# # def schedule(request):
# #     current_user = request.user
# #     schedules = Schedule.objects.filter(bus=current_user).all()
# #     print(schedules)
# #     return render(request,'schedule.html',{'schedules':schedules})
def schedules(request):
    schedules = Schedule.objects.all()
    return render(request,'schedule.html',{'schedules':schedules})

@login_required
def delete_schedule(request,id):
    schedules = Schedule.objects.filter(id=id).delete()

    # db.session.delete(schedules)
    # db.session.commit()

    return redirect('schedules')




def search_results(request):
    '''
    View function to get the the requested departure and arrival locations from the database and display to the user
    '''
    try:
        title = 'Result'

        if ('depature-location' in request.GET and request.GET['depature-location']) and ('arrival-location' in request.GET and request.GET['arrival-location']) and ('travel-date' in request.GET and request.GET['travel-date']):

            # Get the input departure
            search_departure_location = request.GET.get('depature-location').title()

            # Get the input arrival location
            search_arrival_location = request.GET.get('arrival-location').title()

            # Get the input date
            travel_date = request.GET.get('travel-date')

            # Convert string input to date type
            convert_to_date = datetime.strptime(travel_date, '%Y-%m-%d').date()

            # Get the route 
            result_route = Route.get_search_route(search_departure_location,search_arrival_location)
            print(result_route)

            # Check if route exists found
            if result_route != None :
                
                # Schedule with the same depature date
                schedule_with_depature_date = Schedule.get_departure_buses(convert_to_date, result_route.id)

                if len(schedule_with_depature_date) > 0:

                    for schedule in schedule_with_depature_date:

                        estimation_duration = Schedule.get_travel_estimation(schedule.id)

                    return render(request, 'search.html', {'title':title, 'search_departure_location':search_departure_location, 'search_arrival_location':search_arrival_location, 'convert_to_date':convert_to_date, 'buses':schedule_with_depature_date, 'estimation_duration':estimation_duration})

                else:
                    print('no scheduled buses')
                    no_scheduled_bus_message = 'No scheduled buses'

                    return render(request, 'search.html', {'title':title, 'no_scheduled_bus_message':no_scheduled_bus_message, 'search_departure_location':search_departure_location, 'search_arrival_location':search_arrival_location, 'convert_to_date':convert_to_date})

            # Otherwise
            else:
                
                no_route_message = 'Bus route not found'

                return render(request, 'search.html', {'title':title, 'no_route_message':no_route_message, 'search_departure_location':search_departure_location, 'search_arrival_location':search_arrival_location, 'convert_to_date':convert_to_date})
        
    except ObjectDoesNotExist:

        return redirect(Http404)

def SavePayment(request,id):
    saved = False
    data = {}
    hashed = random.randint(0,1000000)
    selected_bus = Schedule.get_single_schedule(id)
    remaining_seats = selected_bus.seats-1
    print(selected_bus)
    if request.method == "POST":
        #Get the posted form
        MyPaymentForm = Payment(request.POST, request.FILES)
        # print(MyPaymentForm.is_valid())
        if MyPaymentForm.is_valid():
            # workers = workers()
            payment = MyPaymentForm.save(commit=False)
            data['amount'] = selected_bus.price
            data['phonenumber'] = payment.phonenumber
            data['clienttime'] = '1556616823718'
            data['action'] = "deposit"
            data['appToken'] = "af11e9eebe55b2032744"
            data['hash'] = hashed
            payment.transaction_code = hashed
            payment.amount = selected_bus.price
            print(data)
            Schedule.objects.filter(id = selected_bus.id).update(seats =remaining_seats)
            payment.save()
            print(payment.id)
            
            # payload = data
            # url = "https://uplus.rw/bridge/"
            # requests.post(url, data=payload)
            
          
            return redirect('response',id=payment.id)
    return render(request,'home.html')


def bus_details(request, bus_schedule_id):
    '''
    View function to display a form for the user to fill to get a ticket
    '''
    try:
        # args = {}

        selected_bus = Schedule.get_single_schedule(bus_schedule_id)

        # title = f'{selected_bus.bus.bus_organisation} Schedule Details'

        estimation_duration = Schedule.get_travel_estimation(bus_schedule_id)

        if request.method == 'POST':
            
            form = TicketForm(request.POST)

            if form.is_valid():
                
                ticket = form.save(commit=False)

                ticket.schedule = selected_bus

                ticket.ticket_number = uuid.uuid4()

                ticket.save()

                ticket_id = ticket.id

                return redirect('pay',id=selected_bus.id)

        else:

            form = Payment()

        # args['form'] = form

        return render(request, 'bus_details.html', {'form':form, 'selected_bus':selected_bus, 'estimation_duration':estimation_duration, 'selected_bus':selected_bus})

    except ObjectDoesNotExist:

         return redirect(Http404)

def generate_view(request, id):
    print(id)
    gotten_ticket = PaymentForm.objects.filter(id=id).first()
    # return render(request,'pdf/ticket.html', {'gotten_ticket':gotten_ticket})
    # gotten_ticket = PaymentForm.objects.filter(id=payment).first()

    pdf = render_to_pdf('pdf/ticket.html', {'gotten_ticket':gotten_ticket})

    if pdf:

        response = HttpResponse(pdf, content_type='application/pdf')

        filename = "Ticket_%s.pdf" %(gotten_ticket.transaction_code)

        content = "inline; filename='%s'"%(filename)

        download = request.GET.get("download")

        if download:

            content = "attachment; filename='%s'"%(filename)

        response['Content-Disposition'] = content

        return response

    return HttpResponse('Not Found')




# @main.route('/delete_schedule/<id>', methods=['GET', 'POST'])
