from django.http import JsonResponse
from common.json import ModelEncoder
from .models import Attendee
from events.models import Conference
from events.api_views import ConferenceListEncoder
import json
from django.views.decorators.http import require_http_methods



class AttendeeListEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "name"
    ]


class AttendeeDetailEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "email",
        "name",
        "company_name",
        "created",
        "conference",
    ]

    encoders = {
        "conference": ConferenceListEncoder(),
    }


@require_http_methods(["GET", "POST"])
def api_list_attendees(request, conference_id):
    if request.method == "GET":
        attendees = Attendee.objects.filter(conference=conference_id)
        return JsonResponse(
            {"attendees": attendees},
            encoder=AttendeeListEncoder,
            safe=False,
        )
    else:
        content = json.loads(request.body)

        try:
            content["conference"] = Conference.objects.get(id=conference_id)
        except Conference.DoesNotExist:
            return JsonResponse(
                {"Message": "Conference Does Not Exist"},
                status=400,
            )

        print(content)

        attendee = Attendee.objects.create(**content)

        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )


@require_http_methods(["GET", "DELETE", "PUT"])
def api_show_attendee(request, pk):
    if request.method == "GET":
        attendee = Attendee.objects.get(id=pk)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Attendee.objects.filter(id=pk).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)

        try:
            content["conference"] = Conference.objects.get(id=content["conference"])
        except Conference.DoesNotExist:
            return JsonResponse(
                {"Message": "Conference Does Not Exist"},
                status=400,
            )
        
        Attendee.objects.filter(id=pk).update(**content)

        attendee = Attendee.objects.get(id=pk)

        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )
