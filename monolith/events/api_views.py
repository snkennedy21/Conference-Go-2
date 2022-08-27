import re
from django.http import JsonResponse
from common.json import ModelEncoder
from .models import Conference, Location, State
from django.views.decorators.http import require_http_methods
import json
from events.acls import get_picture, get_lat_lon, get_weather


class LocationListEncoder(ModelEncoder):
    model = Location
    properties = [
        "name"
    ]

class LocationDetailEncoder(ModelEncoder):
    model = Location
    properties = [
        "name",
        "city",
        "room_count",
        "created",
        "updated",
        "picture_url",
    ]

    def get_extra_data(self, obj):
        return {"state": obj.state.abbreviation}

class ConferenceListEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
    ]

class ConferenceDetailEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
        "description",
        "max_presentations",
        "max_attendees",
        "starts",
        "ends",
        "created",
        "updated",
        "location",
    ]

    encoders = {
        "location": LocationListEncoder(),
    }

    
@require_http_methods(["GET", "POST"])
def api_list_conferences(request):
    if request.method == "GET":
        conferences = Conference.objects.all()
        return JsonResponse(
            {"conferences": conferences},
            encoder=ConferenceListEncoder,
            safe=False,
        )
    else:
        content = json.loads(request.body)

        try:
            location = Location.objects.get(id=content["location"])
            content["location"] = location
        except Location.DoesNotExist:
            return JsonResponse(
                {"Message": "Location Does Not Exist"},
                status=400,
            )


        conference = Conference.objects.create(**content)
        return JsonResponse(
            conference,
            encoder=ConferenceDetailEncoder,
            safe=False,
        )


@require_http_methods(["GET", "DELETE", "PUT"])
def api_show_conference(request, pk):
    if request.method == "GET":
        conference = Conference.objects.get(id=pk)

        city = conference.location.city
        state = conference.location.state
        
        weather = get_weather(city, state)


        return JsonResponse(
            {"conference": conference, "weather": weather},
            encoder=ConferenceDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Conference.objects.filter(id=pk).delete()
        return JsonResponse({"deleted": count > 0})

    else:
        content = json.loads(request.body)

        try:
            location = Location.objects.get(id=content["location"])
            content["location"] = location
        except Location.DoesNotExist:
            return JsonResponse(
                {"Message": "Location Does Not Exist"},
                status=400,
            )
        
        Conference.objects.filter(id=pk).update(**content)
        conference = Conference.objects.get(id=pk)

        return JsonResponse(
            conference,
            encoder=ConferenceDetailEncoder,
            safe=False,
        )
        


@require_http_methods(["GET", "POST"])
def api_list_locations(request):
    if request.method == "GET":
        locations = Location.objects.all()
        return JsonResponse(
            {"locations": locations},
            encoder=LocationListEncoder,
            safe=False,
        )
    else:
        content = json.loads(request.body)

        try:
            state = State.objects.get(abbreviation=content["state"])
            content["state"] = state
        except State.DoesNotExist:
            return JsonResponse({"message": "State Does Not Exist"})


        picture_url = get_picture(content["city"], content['state'])
        content.update(picture_url)

        location = Location.objects.create(**content)

        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
        )


@require_http_methods(["GET", "DELETE", "PUT"])
def api_show_location(request, pk):
    if request.method == "GET":
        location = Location.objects.get(id=pk)
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
        )
    
    elif request.method == "DELETE":
        count, _ = Location.objects.filter(id=pk).delete()
        return JsonResponse({"deleted": count > 0})

    else:
        content = json.loads(request.body)

        try:
            if "state" in content:
                state = State.objects.get(abbreviation=content["state"])
                content["state"] = state
        except State.DoesNotExist:
            return JsonResponse(
                {"message": "State Does Not Exist"},
                status=400,
            )

        Location.objects.filter(id=pk).update(**content)
        location = Location.objects.get(id=pk)

        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
        )

