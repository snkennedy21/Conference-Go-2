from django.http import JsonResponse
from common.json import ModelEncoder
from .models import Presentation
from events.api_views import ConferenceListEncoder


class PresentationListEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "title",
    ]

    def get_extra_data(self, obj):
        return {"status": obj.status.name}


class PresentationDetailEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "presenter_name",
        "company_name",
        "presenter_email",
        "title",
        "synopsis",
        "created",
        "conference",
    ]

    def get_extra_data(self, obj):
        return {"status": obj.status.name}

    encoders = {
        "conference": ConferenceListEncoder(),
    }


def api_list_presentations(request, conference_id):
    presentations = Presentation.objects.filter(conference=conference_id)
    return JsonResponse(
        {"presentations": presentations},
        encoder=PresentationListEncoder,
        safe=False,
    )


def api_show_presentation(request, pk):
    presentation = Presentation.objects.get(id=pk)
    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )
