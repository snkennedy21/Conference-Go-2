from django.http import JsonResponse

from .models import Attendee


def api_list_attendees(request, conference_id):
    response = []
    attendees = Attendee.objects.filter(conference=conference_id)
    for attendee in attendees:
        response.append({
            "name": attendee.name,
            "href": attendee.get_api_url(),
        })
    return JsonResponse({"attendees": response})


def api_show_attendee(request, pk):
    attendee = Attendee.objects.get(id=pk)
    return JsonResponse({
        "email": attendee.email,
        "name": attendee.name,
        "company_name": attendee.company_name,
        "created": attendee.created,
        "conference": {
            "name": attendee.conference.name,
            "href": attendee.conference.get_api_url(),
        }
    })
