from django.http import JsonResponse
from common.json import ModelEncoder
from events.models import Conference
from .models import Presentation, Status
from events.api_views import ConferenceListEncoder
from django.views.decorators.http import require_http_methods
import json
import pika


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


@require_http_methods(["GET", "POST"])
def api_list_presentations(request, conference_id):
    if request.method == "GET":
        presentations = Presentation.objects.filter(conference=conference_id)
        return JsonResponse(
            {"presentations": presentations},
            encoder=PresentationListEncoder,
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
        
        presentation = Presentation.create(**content)
        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )



@require_http_methods(["GET", "DELETE", "PUT"])
def api_show_presentation(request, pk):
    if request.method == "GET":
        presentation = Presentation.objects.get(id=pk)
        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Presentation.objects.filter(id=pk).delete()
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
        
        Presentation.objects.filter(id=pk).update(**content)
        presentation = Presentation.objects.get(id=pk)

        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )


def send_message(presentation, queue):
    presentation_data = {
        "name": presentation.presenter_name,
        "email": presentation.presenter_email,
        "title": presentation.title,
    }
    parameters = pika.ConnectionParameters(host="rabbitmq")
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    channel.basic_publish(
        exchange="",
        routing_key=queue,
        body=json.dumps(presentation_data),
    )
    connection.close()


@require_http_methods(["PUT"])
def api_approve_presentation(request, pk):
    presentation = Presentation.objects.get(id=pk)
    presentation.approve()
    send_message(presentation, "presentation_approvals")
    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )


@require_http_methods(["PUT"])
def api_reject_presentation(request, pk):
    presentation = Presentation.objects.get(id=pk)
    presentation.reject()
    send_message(presentation, "presentation_rejections")
    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )