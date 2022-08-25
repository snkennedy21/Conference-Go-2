from django.http import JsonResponse

from .models import Presentation


def api_list_presentations(request, conference_id):
    presentations = [
        {
            "title": p.title,
            "status": p.status.name,
            "href": p.get_api_url(),
        }
        for p in Presentation.objects.filter(conference=conference_id)
    ]
    return JsonResponse({"presentations": presentations})


def api_show_presentation(request, pk):
    presentation = Presentation.objects.get(id=pk)
    return JsonResponse({
        "presenter_name": presentation.presenter_name,
        "company_name": presentation.company_name,
        "presenter_email": presentation.presenter_email,
        "title": presentation.title,
        "synopsis": presentation.synopsis,
        "created": presentation.created,
        "status": presentation.status.name,
        "conference": {
            "name": presentation.conference.name,
            "href": presentation.conference.get_api_url(),
        }
    })
