from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse

from .models import Flight, Passenger

# Create your views here.
def index(request):
    context = {
        "flights": Flight.objects.all()
    }
    return render(request, "flights/index.html", context)

def flight(request, flight_id):
    try:
        flight = Flight.objects.get(pk = flight_id)
    except Flight.DoesNotExist:
        raise Http404("Flight does not exist.")
    context = {
        "flight": flight,
        "passengers": flight.passengers.all(),
        "nonpassengers": Passenger.objects.exclude(flights=flight).all()
    }
    return render(request, "flights/flight.html", context)

def book(request, flight_id):
    try:
        passenger_id = int(request.POST["passenger"])
        passenger = Passenger.objects.get(pk = passenger_id)
        flight = Flight.objects.get(pk = flight_id)
        address = request.POST["address"]
    except KeyError:
        return render(request, "flights/error.html", {"message": "No selection."})
    except Passenger.DoesNotExist:
        return render(request, "flights/error.html", {"message": "No passenger."})
    except Flight.DoesNotExist:
        return render(request, "flights/error.html", {"message": "No flight."})

    passenger.flights.add(flight)

    url = request.build_absolute_uri(reverse('flight', args=(str(flight.id))))
    html_content = render_to_string(
        "flights/email.html",
        {"passenger": passenger, "flight": flight, "url": url}
    )

    message = EmailMultiAlternatives(
        subject = "Flight Confirmation",
        body = "Your flight has been confirmed",
        to = [address]
    )
    message.attach_alternative(html_content, "text/html")
    message.send()

    return HttpResponseRedirect(reverse("flight", args=[flight_id]))
